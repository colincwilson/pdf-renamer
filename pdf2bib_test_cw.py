# Test pdf2bib: parse files, write bib.
import re, sys
import pdf2bib
from pdf2bib.main import save_bibtex_entries
from pathlib import Path

pdf2bib.config.set('verbose', True)  # Print logging messages.
pdf2bib.config.set('separator', '/')  # Forward slash in paths.
path = Path.home() / 'Downloads/tmp'
result = pdf2bib.pdf2bib(path)
print(result)
# Each member of results is None or a dictionary with many fields, ex.:
# 'identifier': '10.1007/s10849-018-9270-x', 'identifier_type': 'DOI', 'path': '/home/colin/Downloads/tmp/Jardine_ExpressivityAutosegmentalGrammars.pdf', ...

bibtex_file = 'out.bib'  # NB. relative to path.
save_bibtex_entries(bibtex_file, result, False)
