#!/usr/bin/env python3

from pybtex.database import parse_file
from textdistance import levenshtein as lev
import argparse
import json
import aiohttp
import asyncio
import datetime
import re
import pdb

def lower_lev(stra, strb):
    return lev(stra.lower(),strb.lower())
parser = argparse.ArgumentParser(description="Replenish doi for a given bib")
parser.add_argument('-n', '--num-workers', type=int, default=10, help='number of workers to send http request (default: %(default)s)')
parser.add_argument('--max-rps', type=int, default=10, help='max number of request per second (default: %(default)s)')
parser.add_argument('inbib', type=str, help="input bib file")
parser.add_argument('outbib', type=str, help="output bib file")
args = parser.parse_args()

stat_counters = {
        'update' : 0,  # the search returns highly matched results, doi updated
        'error' : 0,   # the search does not return valid results
        'warning' : 0, # the search returned results but ignored due to high edit-distance
        'skip' : 0,    # the search was skipped because the entry should not have any doi
        'haddoi': 0,   # the search was skipped because the entry already had a doi
}

bib_data = parse_file(args.inbib)
per_worker_delay = datetime.timedelta(seconds=(args.max_rps/args.num_workers))

title_trans = str.maketrans({
    '$': '', '\\': '',
    '{': '', '}': ''
})
latex_comamnd_pat = r'\\[a-zA-Z0-9]+([^a-zA-Z0-9])'
latex_command_repl = r'\1'
def title_canonical(title: str) -> str:
    title = re.sub(latex_comamnd_pat, latex_command_repl, title)
    return title.translate(title_trans)

async def async_main(args, bib_data, stat_counters):
    # each item is (key: str, entry: pybtex)
    bib_queue = asyncio.Queue()
    for key, entry in bib_data.entries.items():
        if entry.type == 'patent':
            print(f"Skip ('patent'): {key}")
            stat_counters['skip'] += 1
            continue
        if entry.type in {'misc', 'electronic'}:
            skip = False
            for skiptype in ['howpublished', 'url']:
                if skiptype in entry.fields:
                    print(f"Skip ({skiptype}): {key}")
                    stat_counters['skip'] += 1
                    skip = True
                    break
            if skip:
                continue
        if len(entry.persons) == 0:
            print(f"Skip (no author): {key}")
            stat_counters['skip'] += 1
            continue
        if 'doi' in entry.fields:
            print(f"Skip (had doi): {key}")
            stat_counters['haddoi'] += 1
            continue
        await bib_queue.put((key, entry))
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[updateBibWithDOI(session, bib_queue, stat_counters) for i in range(args.num_workers)])

async def updateBibWithDOI(aiosession, bib_queue, stat_counters):
    while not bib_queue.empty():
        start_time = datetime.datetime.now()
        key, entry = await bib_queue.get()
        title = title_canonical(entry.fields['title'])
        # This is the API used in https://zbib.org/
        async with aiosession.post("https://t0guvf0w17.execute-api.us-east-1.amazonaws.com/Prod/search",
                data=title.encode('utf-8'),
                headers={
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain",
                    "Origin": "https://zbib.org",
                    "Pragma": "no-cache",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
                    },
                cookies={}) as res:
            resj = await res.json()
            if len(resj) == 0:
                print(f"Error# not found in zlib; key: {key}; title:\"{title}\"")
                stat_counters['error'] += 1
                continue
            elif not res.ok:
                print(f"Error# request error; key: {key}; title: \"{title}\"")
                stat_counters['error'] += 1
                continue
            ranked_result = sorted(resj.keys(), key=lambda k: lower_lev(title, title_canonical(resj[k]['title'])))
            doi = ranked_result[0]
            doi_title = resj[doi]['title']
            if lower_lev(title, title_canonical(doi_title)) > 5:
                print(f"Warning# high edit distance; key: {key};")
                print(f"\ttitle : \"{title}\";")
                print(f"\tresult: \"{doi_title}\";")
                print(f"\tdoi: {doi}")
                stat_counters['warning'] += 1
                continue
            print(f"Found; key: {key}; title: \"{title}\"; doi: {doi}".format(key, title, doi))
            entry.fields['doi'] = doi
            stat_counters['update'] += 1
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        if per_worker_delay > elapsed_time:
            await asyncio.sleep((per_worker_delay - elapsed_time).total_seconds())

asyncio.run(async_main(args, bib_data, stat_counters))

if stat_counters['update'] > 0:
    bib_data.to_file(args.outbib, 'bibtex')
else:
    print(f"Did not find any updates on DOI. Do not write to {args.outbib}")

print(f"statistics: {json.dumps(stat_counters, indent=2)}")
