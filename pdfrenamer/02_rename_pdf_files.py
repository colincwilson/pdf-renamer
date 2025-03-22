# Rename pdf files using bibtex entries (filename_old -> filename_new).
# NB. Edit bibtex file before running!
# CW, March 2025

import sys, os
import argparse
import bibtexparser
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description=
        "Automatically rename pdf files using bibtex entries (filename_old -> filename_new).",
        epilog="",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument( \
        "--path",
        help="Path of the folder containing pdf files.")
    parser.add_argument( \
        "--bibtex_file",
        help="Path of the bibtex file.")
    parser.add_argument( \
        "--dry_run",
        help="Describe but do not execute file renaming.",
        action="store_true")

    args = parser.parse_args()
    print(args)

    # # # # # # # # # #

    target_dir = Path(args.path)
    bibtex_file = args.bibtex_file
    dry_run = args.dry_run

    if not bibtex_file:
        bibtex_file = target_dir / (str(Path(target_dir).name) + '.bib')

    with open(bibtex_file, 'r') as f:
        bibtex_dat = bibtexparser.load(f)

    for bibtex_entry in bibtex_dat.entries:
        folder = bibtex_entry.get('folder')
        filename_old = bibtex_entry.get('filename_old')
        filename_new = bibtex_entry.get('filename_new')
        try:
            print(
                f'Renaming {folder}/{filename_old} -> {folder}/{filename_new}\n'
            )
            if dry_run:
                continue
            Path(f'{folder}/{filename_old}').move(f'{folder}/{filename_new}')
        except:
            continue
        break


if __name__ == '__main__':
    main()
