DIR=/home/cwilso23/Notes/SignLanguage/tmp
cp "$DIR/tmp.pdf" "$DIR/tmp.pdf.bkp"
pdfrenamer "$DIR/tmp.pdf" -f "{A3etal}_{T}{YYYY}"
mv "$DIR/tmp.pdf.bkp" "$DIR/tmp.pdf"