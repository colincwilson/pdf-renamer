DIR="$HOME/Projects/SignTracking/papers_more"
#cp "$DIR/tmp.pdf" "$DIR/tmp.pdf.bkp"
python pdfrenamer/main.py "$DIR" -f "{A3etal}_{T}{YYYY}" --dry_run --force_rename
#mv "$DIR/tmp.pdf.bkp" "$DIR/tmp.pdf"