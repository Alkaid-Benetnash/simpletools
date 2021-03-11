from pybtex.database import parse_file
from textdistance import levenshtein as lev
import requests
import argparse

def lower_lev(stra, strb):
    return lev(stra.lower(),strb.lower())
parser = argparse.ArgumentParser(description="Replenish doi for a given bib")
parser.add_argument('inbib', type=str, help="input bib file")
parser.add_argument('outbib', type=str, help="output bib file")
args = parser.parse_args()

bib_data = parse_file(args.inbib)

for key, entry in bib_data.entries.items():
    if len(entry.persons) > 0 and 'doi' not in entry.fields:
        title = entry.fields['title'].replace('{','').replace('}','')
        # This is the API used in https://zbib.org/
        res=requests.post("https://t0guvf0w17.execute-api.us-east-1.amazonaws.com/Prod/search",
                data=title,
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
            print("Error# not found in zlib#{}#\"{}\"".format(key,title))
            continue
        elif not res.ok:
            print("Error# request error#{}#\"{}\"".format(key,title))
            continue
        ranked_result = sorted(resj.keys(), key=lambda k: lower_lev(title,resj[k]['title']))
        doi = ranked_result[0]
        if lower_lev(title, resj[doi]['title']) > 5:
            print("Warning# high edit distance#{}#\"{}\"#{}".format(key,title, doi))
            continue
        print("Found# {}#\"{}\"#{}".format(key, title, doi))
        entry.fields['doi'] = doi
bib_data.to_file(args.outbib, 'bibtex')
