#!/usr/bin/env python3

from pybtex.database import parse_file
from textdistance import levenshtein as lev
import requests
import argparse
import json

def lower_lev(stra, strb):
    return lev(stra.lower(),strb.lower())
parser = argparse.ArgumentParser(description="Replenish doi for a given bib")
parser.add_argument('inbib', type=str, help="input bib file")
parser.add_argument('outbib', type=str, help="output bib file")
args = parser.parse_args()

stat_counters = {
        'update' : 0,  # the search returns highly matched results, doi updated
        'error' : 0,   # the search does not return valid results
        'warning' : 0, # the search returned results but ignored due to high edit-distance
        'skip' : 0,    # the search was skipped
}

bib_data = parse_file(args.inbib)

for key, entry in bib_data.entries.items():
    if entry.type == 'patent':
        print(f"Skip ('patent'): {key}")
        stat_counters['skip'] += 1
        continue
    if entry.type == 'misc':
        skip = False
        for skiptype in ['howpublished', 'url']:
            if skiptype in entry.fields:
                print(f"Skip ({skiptype}): {key}")
                stat_counters['skip'] += 1
                skip = True
                break
        if skip:
            continue
    if len(entry.persons) > 0 and 'doi' not in entry.fields:
        title = entry.fields['title'].replace('{','').replace('}','')
        # This is the API used in https://zbib.org/
        res=requests.post("https://t0guvf0w17.execute-api.us-east-1.amazonaws.com/Prod/search",
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
                cookies={},
        )
        resj = res.json()
        if len(resj) == 0:
            print(f"Error# not found in zlib; key: {key}; title:\"{title}\"")
            stat_counters['error'] += 1
            continue
        elif not res.ok:
            print(f"Error# request error; key: {key}; title: \"{title}\"")
            stat_counters['error'] += 1
            continue
        ranked_result = sorted(resj.keys(), key=lambda k: lower_lev(title,resj[k]['title']))
        doi = ranked_result[0]
        doi_title = resj[doi]['title']
        if lower_lev(title, doi_title) > 5:
            print(f"Warning# high edit distance; key: {key};")
            print(f"\ttitle : \"{title}\";")
            print(f"\tresult: \"{doi_title}\";")
            print(f"\tdoi: {doi}")
            stat_counters['warning'] += 1
            continue
        print(f"Found; key: {key}; title: \"{title}\"; doi: {doi}".format(key, title, doi))
        entry.fields['doi'] = doi
        stat_counters['update'] += 1
if stat_counters['update'] > 0:
    bib_data.to_file(args.outbib, 'bibtex')
else:
    print(f"Did not find any updates on DOI. Do not write to {args.outbib}")

print(f"statistics: {json.dumps(stat_counters, indent=2)}")
