import logging

# Setup logging
logger = logging.getLogger("pdf-renamer")
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[pdf-renamer]: %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False

from .config import config

config.ReadParamsINIfile()

# Quick-and-dirty method to ensure that the verbosity of pdf2doi
# is set according to the current value of config.get('verbose')
config.set('verbose', config.get('verbose'))

from .main import get_renaming_info, build_filename
from .filename_creators import *
