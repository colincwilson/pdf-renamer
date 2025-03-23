# Automatically make bibtex entries for pdf files in a folder,
# including renaming suggestions filename_old -> filename_new.
# CW, March 2025

import sys, os
import argparse
import logging
import bibtexparser
import pdf2bib
import pdf2doi
import pdfrenamer.config as config
import polars as pl
from pathlib import Path
from pdfrenamer.filename_creators import \
    (build_filename, AllowedTags, check_format_is_valid)
import traceback

logger = logging.getLogger("pdf-renamer")

# # # # # # # # # #


def get_bibtex_entries(target, bibtex_file, todo_dir, format=None, tags=None):
    """
    Create bibtex entries (with renaming suggestions) in the
    specified format for all pdf files in the target path.
    Paper info (title, authors, etc.) is obtained via the
    library pdf2bib (which in turns uses pdf2doi).
    If the global settingcheck_subfolders is set to True,
    it also renames pdf files in all subfolders (recursively).
    Move pdf files for which bibtex entries cannot be found
    to `todo` subfolder.

    Parameters
    ----------
    target : string
        Relative or absolute path of the target .pdf file or directory
    Returns
    -------
    results, dictionary or list of dictionaries (or None if an error occured)
        The output is a single dictionary if target is a file, or a list of dictionaries if target is a directory, each element of the list describing one file. Each dictionary has the following keys
        result['path_orig'] : path of the pdf file (with the original filename)
        result['path_new'] : path of the pdf file, with the new filename, or None if it was not possible to generate a new filename
        result['identifier'] : DOI or other identifier (or None if nothing is found)
        result['identifier_type'] : String specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] : Additional info on the paper. If config.get('webvalidation') = True, then result['validation_info']
                                      will typically contain raw bibtex data for this paper. Otherwise it will just contain True 
        result['path'] : Path of the pdf file
        result['method'] : Method used by pdf2doi to find the identifier
        result['metadata'] : Dictionary containing bibtex info
        result['bibtex'] : A string containing a valid bibtex entry
    """

    # Setup logging.
    logger = logging.getLogger("pdf-renamer")

    # Get default format if needed.
    if not format:
        format = config.get('format')

    # If tags is a valid variable, the format was already checked
    # by a previous call to this function.
    if not tags:
        tags = check_format_is_valid(format)
        if tags == None:
            return None

    # Check if path is valid.
    if not (os.path.exists(target)):
        logger.error(f"{target} is not a valid path to a file or a directory.")
        return

    # Process all pdf files in dictionary target;
    # if config.get('check_subfolders')==True, recursively call
    # this function for all each subfolder in target.
    if os.path.isdir(target):
        logger.info(
            f"Looking for pdf files and subfolders in the folder {target} ...")
        # Make sure the path ends with "\" or "/" (according to the OS)
        if not (target.endswith(os.path.sep)):
            target = target + os.path.sep

        # List all the pdf files in target folder
        # (and optionally subfolders).
        pdf_files = sorted([f for f in os.listdir(target) \
            if (f.lower()).endswith('.pdf')])
        subfolders = sorted([f.path for f in os.scandir(target) \
            if f.is_dir()])

        nfiles = len(pdf_files)
        if nfiles == 0:
            logger.error("No pdf file found in this folder.")
        else:
            logger.info(f"Found {nfiles} pdf file(s).")

            # List to store dictionaries, one per pdf file.
            files_processed = []
            for pdf_file in pdf_files:
                logger.info("................")
                pdf_file = target + pdf_file
                result = get_bibtex_entry(pdf_file,
                                          bibtex_file,
                                          todo_dir,
                                          format=format,
                                          tags=tags)
                files_processed.append(result)
            logger.info("................")

        # If there are subfolders and config.get('check_subfolders')
        # is set, call this function on each subfolder.
        nsubfolders = len(subfolders)
        if nsubfolders:
            logger.info(f"Found {nsubfolders} subfolder(s)")
            if config.get('check_subfolders'):
                logger.info("Exploring subfolders...")
                for subfolder in subfolders:
                    result = get_bibtex_entries(subfolder,
                                                bibtex_file,
                                                todo_dir,
                                                format=format,
                                                tags=tags)
                    files_processed.extend(result)
            else:
                logger.info(
                    "The subfolder(s) will not be scanned because the parameter check_subfolders is set to False."
                    +
                    " When using this script from command line, use the option -sf to explore also subfolders."
                )
            logger.info("................")

        return files_processed

    # Process one pdf file.
    try:
        result = get_bibtex_entry(target,
                                  bibtex_file,
                                  todo_dir,
                                  format=format,
                                  tags=tags)
    except:
        result = None

    return result


def get_bibtex_entry(filename, bibtex_file, todo_dir, format=None, tags=None):
    """
    Automatically create bibtex entry for one pdf file. If bibtex entry
    cannot be created, move file to `todo` subfolder.
    """
    logger.info(f"File: {filename}")
    if not os.path.exists(filename):
        logger.error(f"Skipping file: Invalid path ({filename}).")
        return None
    if not (filename.lower()).endswith('.pdf'):
        logger.error(f"Skipping file: Does not have .pdf extension.")
        return None

    if not config.get('overwrite') \
        and check_already_processed(filename, format):
        logger.info(f"Skipping file: already processed ({filename}).")
        return None

    # Use pdf2bib to retrieve info about the file.
    logger.info(
        f"Calling the pdf2bib library to retrieve the bibtex info of this file."
    )
    try:
        result = pdf2bib.pdf2bib_singlefile(filename)
        metadata = result['metadata'].copy()
        metadata_str = "\n\t" + "\n\t".join(
            [f"{key} = \"{metadata[key]}\"" for key in metadata.keys()])
        logger.info("Found the following data:" + metadata_str)

        # Generate new filename.
        filename_new = build_filename(metadata, format, tags)
        # Add extension from old filename.
        ext = os.path.splitext(filename)[-1].lower()
        directory = Path(filename).parent
        path_new = str(directory) + os.path.sep + filename_new + ext
    except Exception as e:
        logger.error(
            f'Error in using pdf2bib to process or creating new file name for {filename}.'
        )
        logger.error(str(e))
        result = {}
        path_new = ""

    # Write entry to bibtex file, or move file to
    # todo subfolder if entry could not be created.
    result['folder'] = folder = str(Path(filename).parent)
    result['filename_old'] = filename_old = str(Path(filename).name)
    result['path_new'] = path_new
    if path_new != "":
        result['filename_new'] = filename_new = \
            str(Path(result['path_new']).name)
    else:
        result['filename_new'] = filename_new = ""

    if result.get('identifier') and result.get('bibtex'):
        entry = bibtexparser.loads(result['bibtex'])
        entry.entries[0]['folder'] = folder
        entry.entries[0]['filename_old'] = filename_old
        entry.entries[0]['filename_new'] = filename_new
        entry_str = bibtexparser.dumps(entry)
        with open(bibtex_file, 'a') as f:
            f.writelines(f'{entry_str}\n')
            f.close()
        mark_file_processed(filename, format)
    else:
        Path(f'{folder}/{filename_old}').rename( \
            f'{folder}/todo/{filename_old}')

    return result


def check_already_processed(filename, format):
    """
    Check pdf metadata to see if it was already
    processed by this script / in this format.
    """
    flag = False
    try:
        with open(filename, 'rb') as f:
            infos = pdf2doi.get_pdf_info(f)
            if '/pdfrenamer_nameformat' in infos.keys():
                if infos['/pdfrenamer_nameformat'] == format:
                    flag = True
    except Exception as e:
        logger.exception(f"File processing error: {e}")
        flag = None
    return flag


def mark_file_processed(filename, format):
    """
    Add pdf metadata indicating that it has been
    processed by this script / in this format.
    """
    pdf2doi.add_metadata( \
        filename,
        '/pdfrenamer_nameformat',
        format)


def add_abbreviations(path_abbreviation_file):
    """
    Append contents of the text file specified by path_abbreviation_file
    to the beginning of the file UserDefinedAbbreviations.txt.
    """
    if not (os.path.exists(path_abbreviation_file)):
        logger.error(
            f"{path_abbreviation_file} is not a valid path to a file.")
        return

    logger.info(f"Loading the file {path_abbreviation_file}...")
    try:
        with open(path_abbreviation_file, 'r') as new_abbreviation_file:
            new_abbreviation = new_abbreviation_file.read()
    except Exception as e:
        logger.error('Some error occured while loading this file: \n ' +
                     str(e))
        return

    logger.info(
        f"Adding the content of the file {path_abbreviation_file} to the user-specified journal abbreviations..."
    )

    try:
        path_current_directory = os.path.dirname(__file__)
        path_UserDefinedAbbreviations = os.path.join(
            path_current_directory, 'UserDefinedAbbreviations.txt')
        with open(path_UserDefinedAbbreviations,
                  'r') as UserDefinedAbbreviations_oldfile:
            UserDefinedAbbreviations_old = UserDefinedAbbreviations_oldfile.read(
            )
        with open(path_UserDefinedAbbreviations,
                  'w') as UserDefinedAbbreviations_newfile:
            UserDefinedAbbreviations_newfile.write(new_abbreviation)
            UserDefinedAbbreviations_newfile.write('\n')
            UserDefinedAbbreviations_newfile.write(
                UserDefinedAbbreviations_old)
    except Exception as e:
        logger.error('Some error occured: \n ' + str(e))
        return

    logger.info(f"The new journal abbreviations were correctly added.")


def main():
    parser = argparse.ArgumentParser(
        description=
        "Automatically create bibtex entries for pdf files of scientific publications by retrieving their identifiers (e.g., DOI or arxiv ID) and looking up their bibtext entries.",
        epilog="",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument( \
        "path",
        help="Path of the folder containing pdf files.",
        metavar="path",
        nargs='*')
    parser.add_argument( \
        "-s",
        "--decrease_verbose",
        help=
        "Decrease verbosity. By default (i.e. when not using -s), all steps performed by pdf-renamer, pdf2dbib and pdf2doi are documented.",
        action="store_true")
    parser.add_argument( \
        '-f',
        help=
        f"Format of the new filename. Default = \"{config.get('format')}\".\n"
        + "Valid tags:\n" +
        "\n".join([key + val for key, val in AllowedTags.items()]),
        action="store",
        dest="format",
        type=str,
        default=config.get('format'))
    parser.add_argument( \
        "-sf",
        "--sub_folders",
        help=
        f"Rename also pdf files contained in subfolders of target folder. Default = \"{config.get('check_subfolders')}\".",
        action="store_true")
    parser.add_argument( \
        '-max_length_authors',
        help=
        f"Sets the maximum length of any string related to authors (default={str(config.get('max_length_authors'))}).",
        action="store",
        dest="max_length_authors",
        type=int,
        default=config.get('max_length_authors'))
    parser.add_argument( \
        '-max_length_filename',
        help=
        f"Sets the maximum length of any generated filename. Any filename longer than this will be truncated (default={str(config.get('max_length_filename'))}).",
        action="store",
        dest="max_length_filename",
        type=int,
        default=config.get('max_length_filename'))
    parser.add_argument( \
        '-max_words_title',
        help=
        f"Sets the maximum number of words from the paper title to use for the filename (default={str(config.get('max_words_title'))}).",
        action="store",
        dest="max_words_title",
        type=int,
        default=config.get('max_words_title'))
    parser.add_argument( \
        '-case',
        help=
        f"Possible values are 'camel', 'snake', 'kebab', 'none' (default={str(config.get('case'))}). \n"
        +
        "If different from 'none', converts each tag string into either 'camel' (e.g., LoremIpsumDolorSitAmet), 'snake' (e.g., Lorem_ipsum_dolor_sit_amet), or 'kebab' case (e.g., Lorem-ipsum-dolor-sit-amet). \n"
        +
        "Note: this will not affect any punctuation symbol or space contained in the filename format by the user.",
        action="store",
        dest="case",
        type=str,
        default=config.get('case'))
    parser.add_argument( \
        "-add_abbreviation_file",
        help=
        "The content of the text file specified by PATH_ABBREVIATION_FILE will be added to the user list of journal abbreviations.\n"
        +
        "Each row of the text file must have the format \'FULL NAME = ABBREVIATION\'.",
        action="store",
        dest="path_abbreviation_file",
        type=str)
    parser.add_argument( \
        "-sd",
        "--set_default",
        help=
        f"By adding this command, any value specified (in this same command) for the filename format (-f),\n"
        +
        "max length of author string (-max_length_authors), max length of filename string (-max_length_filename),\n"
        +
        "max number of title words (-max_words_title), and case (-case) will be also stored as default value(s) for the future.",
        action="store_true")
    parser.add_argument( \
        "-o",
        "--overwrite",
        help=
        f"By default, pdf files for which bibtex entries have already been created (as indicated by pdf metadata) are skipped. Set this flag to process all files instead.",
        action="store_true")

    args = parser.parse_args()
    print(args)

    # # # # # # # # # #

    # Setup logging: store the desired verbosity level in
    # global config of pdf-renamer; this also automatically
    # updates the pdf2bib and pdf2doi logger levels.
    config.set('verbose', not (args.decrease_verbose))
    logger = logging.getLogger("pdf-renamer")

    if args.path_abbreviation_file:
        add_abbreviations(args.path_abbreviation_file)
        return

    if (check_format_is_valid(args.format)):
        config.set('format', args.format)

    if (isinstance(args.max_length_authors, int)
            and args.max_length_authors > 0):
        config.set('max_length_authors', args.max_length_authors)
    else:
        logger.error(
            f"The specified value for max_length_authors is not valid.")

    if (isinstance(args.max_length_filename, int)
            and args.max_length_filename > 0):
        config.set('max_length_filename', args.max_length_filename)
    else:
        logger.error(
            f"The specified value for max_length_filename is not valid.")
    config.set('check_subfolders', args.sub_folders)

    if (isinstance(args.max_words_title, int) and args.max_words_title > 0):
        config.set('max_words_title', args.max_words_title)
    else:
        logger.error(f"The specified value for max_words_title is not valid.")

    if (isinstance(args.case, str)
            and (args.case in ['camel', 'snake', 'kebab', 'none'])):
        config.set('case', args.case)
    else:
        logger.error(f"The specified value for case is not valid.")
        return

    config.set('check_subfolders', args.sub_folders)
    config.set('overwrite', args.overwrite)

    if args.set_default:
        logger.info(
            "Storing the settings specified by the user (if any is valid) as default values..."
        )
        config.WriteParamsINIfile()
        logger.info("Done.")

    # Ensure that 'path' is considered a required parameter.
    if isinstance(args.path, list):
        if len(args.path) > 0:
            target = args.path[0]
        else:
            target = ""
    else:
        target = args.path
    if target == "" and not (args.set_default):
        print(
            "pdfrenamer: error: the following arguments are required: path. Type \'pdfrenamer --h\' for a list of commands."
        )

    # Exit if the user forgot to specify a target or used the
    # -sd command to set default values only.
    if target == "":
        return

    # Bibtex file for pdf entries.
    if os.path.isdir(target):
        target_dir = Path(target)
    else:
        target_dir = Path(target).parent
    bibtex_file = target_dir / (str(Path(target_dir).name) + '.bib')
    if bibtex_file.exists():
        print(f'\nWarning: Bibtex file already exists ({bibtex_file}).')
        resp = input(f'Warning: Press enter to continue or ctrl-z to quit.\n')

    # Subfolder for files that cannot be renamed.
    todo_dir = target_dir / 'todo'
    try:
        todo_dir.mkdir(exist_ok=True)
    except:
        print(f'Stopping: could not create todo subfilder.')
        sys.exit(0)

    # Verbosity.
    if args.decrease_verbose:
        print(
            f"(All intermediate output will be suppressed. To see additional output, do not use the command -s)"
        )

    # # # # # # # # # #

    # Get renaming info for all pdfs in target.
    results = get_bibtex_entries(target=target,
                                 bibtex_file=bibtex_file,
                                 todo_dir=todo_dir)

    return


if __name__ == '__main__':
    main()
