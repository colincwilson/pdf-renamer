# Conda environment

Use within py3_13 environment.

~~pdfrenamer; python 3.12~~

# Usage

DIR="$HOME/Projects/SignTracking/papers_more"

python pdfrenamer/main.py "$DIR" -f "{A3etal}_{T}{YYYY}" --dry_run --force_rename

# Dependencies

<https://github.com/MicheleCotrufo/pdf2doi>

<https://github.com/MicheleCotrufo/pdf2bib>

(and their dependencies)

# Editable local installations

python -m pip install -e ~/Library/Python/pdf2doi # updated requirements.txt with pymupdf 1.24.7

python -m pip install -e ~/Library/Python/pdf2bib

# Proposed pipeline

- Identify folder containing pdf files to be renamed.

- Create subfolders `out` and `miss`.

- Process each pdf with pdf2bib, marking successes and failures; also write .bib file for successes.

- Automatically rename success pdfs, but allow user to override new name with streamlit UI.

- Move original pdf files to `miss` or `orig`.
