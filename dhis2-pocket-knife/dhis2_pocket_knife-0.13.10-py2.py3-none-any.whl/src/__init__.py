import os

import logging
import logzero
from logzero import logger

LOGGING_TO_FILE = False

if LOGGING_TO_FILE:
    logfilename = '/var/log/dhis2-pk.log'

    # different loglevel for the file handler
    logzero.logfile(logfilename, loglevel=logging.ERROR)
else:
    logzero.logfile(None)

formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: %(message)s')
logzero.formatter(formatter)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
