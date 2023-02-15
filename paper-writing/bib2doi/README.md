# bib2doi

Sometimes publisher requires you to provide a DOI for each item in the References section (if possible). This tool can help you add doi to existing bib entries.

### Install

```bash
pip install -r requirements.txt
```

### Usage

```bash
python3 bib2doi.py in.bib out.bib
```

In `stdout`, the tool will report whether it is able to find a matching doi for each bib entry. The `out.bib` will have new `doi` fields inserted to all bib entries when available.

### TODO

1. Support new API. It currently uses the backend API of [zbib](https://zbib.org). The API of [crossref.org](https://github.com/CrossRef/rest-api-doc) should be better.
2. Switch the bibtex engine to https://github.com/sciunto-org/python-bibtexparser
