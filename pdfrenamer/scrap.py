def rename_file(old_path, new_path, ext):
    """
    Rename file old_path -> new_path, adding an incremental number
    if another file with the same name already exists in the same
    folder (e.g. "filename.pdf" becomes "filename (2).pdf")
    """

    if not os.path.exists(old_path):
        raise ValueError(f"The file {old_path} does not exist.")
    i = 1
    while True:
        new_path_ = new_path.removesuffix(ext) + \
            (f" ({i})" if i > 1 else "") + ext
        if config.get('dry_run'):
            return new_path_
        if os.path.exists(new_path_):
            i = i + 1
            continue
        else:
            os.rename(old_path, new_path_)
            return new_path_

        logger.info(f"The new file name is {new_path}.")
        if (filename == new_path) and not config.get('force_rename'):
            logger.info(
                "The new file name is identical to the old one. Nothing will be changed."
            )
            pdf2doi.add_metadata( \
                filename,
                '/pdfrenamer_nameformat',
                format)
            result['path_new'] = new_path
        else:
            try:
                new_path_renamed = rename_file( \
                    filename, new_path, ext)
                logger.info(f"File renamed correctly.")
                if not config.get('dry_run'):
                    pdf2doi.add_metadata( \
                        new_path_renamed,
                        '/pdfrenamer_nameformat',
                        format)
                if not (new_path == new_path_renamed):
                    logger.info(
                        f"(Note: Another file with the same name was already present in the same folder, so a numerical index was added at the end)."
                    )
                result['path_new'] = new_path_renamed
            except Exception as e:
                logger.error(
                    'Some error occured while trying to rename this file: \n '
                    + str(e))
                result['path_new'] = None

    # Exit if no results are available (e.g., when target
    # is not a valid file or directory).
    if results == None:
        return

    if not isinstance(results, list):
        results = [results]

    sys.exit(0)

    # Report results.
    # Ensure that director target ends with "/" or "\" (OS dependent).
    if os.path.isdir(target):
        target = os.path.join(target, '')
    # Get path of target (if directory, main_path == target).
    main_path = os.path.dirname(target)

    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    print(Fore.RED + "Summaries of changes done:")

    counter = 0
    counter_identifier_notfound = 0

    for result in results:
        if result and result['identifier'] and result['path_new']:
            if not (result['path_orig'] == result['path_new']) \
                or config.get('force_rename') or config.get('dry_run'):
                print(Fore.YELLOW +
                      f"{os.path.relpath(result['path_orig'], main_path)}")
                print(Fore.MAGENTA +
                      f"---> {os.path.relpath(result['path_new'], main_path)}")
                counter = counter + 1
        elif not (result['identifier']):
            counter_identifier_notfound = counter_identifier_notfound + 1

    if counter > 0:
        print(f"Found renaming info for {counter} file(s).")
    else:
        print("No renaming info found.")

    if counter_identifier_notfound > 0:
        print(
            Fore.RED +
            "The following pdf files could not be renamed because it was not possile to automatically find "
            +
            "the publication identifier (DOI or arXiv ID). Try to manually add a valid identifier to each file via "
            +
            "the command \"pdf2doi 'filename.pdf' -id 'valid_identifier'\" and then run again pdf-renamer."
        )
        for result in results:
            if not (result['identifier']):
                print(f"{result['path_orig']}")

    # parser.add_argument( \
    #     "-install--right--click",
    #     dest="install_right_click",
    #     action="store_true",
    #     help=
    #     f"Add a shortcut to pdf-renamer in the right-click context menu of Windows. You can rename a single pdf file (or all pdf files in a folder) by just right clicking on it!\n"
    #     + "NOTE: this feature is only available on Windows.")
    # parser.add_argument( \
    #     "-uninstall--right--click",
    #     dest="uninstall_right_click",
    #     action="store_true",
    #     help=
    #     "Uninstall the right-click context menu functionalities. NOTE: this feature is only available on Windows."
    # )

    # #If the command -install--right--click was specified, it sets the right keys in the system registry
    # if args.install_right_click:
    #     config.set('verbose', True)
    #     import pdfrenamer.utils_registry as utils_registry
    #     utils_registry.install_right_click()
    #     return
    # if args.uninstall_right_click:
    #     config.set('verbose', True)
    #     import pdfrenamer.utils_registry as utils_registry
    #     utils_registry.uninstall_right_click()
    #     return
