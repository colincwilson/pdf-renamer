# Conda environment

Use within py3_13 environment.

~~pdfrenamer; python 3.12~~

# Usage

DIR="$HOME/Projects/SignTracking/papers_more"

python pdfrenamer/main.py "$DIR" -f "{A3etal}_{T}{YYYY}"

# Dependencies

<https://github.com/MicheleCotrufo/pdf2doi>

<https://github.com/MicheleCotrufo/pdf2bib>

(and their dependencies)

# Editable local installation of dependencies

python -m pip install -e ~/Library/Python/pdf2doi # updated requirements.txt with pymupdf 1.24.7

python -m pip install -e ~/Library/Python/pdf2bib

# Pipeline

### Specify director of pdf files

DIR="$HOME/folder_containing_pdfs"

### Make bibtex file with entries that include suggested renaming (filename_old -> filename_new), mark files with bibtex entries as processed, move files without bibtex entries to `todo` subfolder

python pdfrenamer/01_make_bibtex.py "$DIR" -f "{A3etal}_{T}{YYYY}" [--overwrite]

### Manually edit bibtex file

### Rename files as specified in edited bibtex

python pdfrenamer/02_rename_files.py "$DIR"

# Alternatives

<https://github.com/perrette/papers>

Ex. Extract metadata from pdf with: `papers extract esd-4-11-2013.pdf`

-- may be more accurate than pdf2bib / pdf2doi

Ex. Add entry to bibtex file and put renamed copy of file in folder: `papers add entry.bib --bibtex papers.bib --attachment esd-4-11-2013.pdf --rename --copy`
