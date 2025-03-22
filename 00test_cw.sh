DIR="$HOME/Projects/SignTracking/papers_more"
#cp "$DIR/tmp.pdf" "$DIR/tmp.pdf.bkp"
python pdfrenamer/01_make_bibtex_file.py "$DIR" -f "{A3etal}_{T}{YYYY}" --overwrite
#mv "$DIR/tmp.pdf.bkp" "$DIR/tmp.pdf"

python pdfrenamer/02_rename_pdf_files.py "$DIR" --dry_run