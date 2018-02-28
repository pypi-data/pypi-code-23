#!/usr/bin/env python3
import logging, datetime

logger = logging.getLogger(__name__)

def logArg(x):
    return {
        'talk': logging.DEBUG,
        'info': logging.INFO,
        'quiet': logging.NOTSET
    }.get(x, logging.NOTSET) 
    # default = NOTSET

def set_up_logging(arg):
    level = logArg(arg)

    date = datetime.date.today().strftime("%d%b%Y")
    LogName = "Pics2WordLog_" + date + ".txt"
    logging.basicConfig(filename=LogName,level=level,format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

    ch = logging.StreamHandler()
    logger.addHandler(ch)