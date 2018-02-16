from __future__ import unicode_literals, print_function
import logging
import logging.config
import sys

logger = logging.getLogger(__name__)


def log_setup(config):
    """ set logging
    """

    level = config['log_level']
    foreground = config['foreground']

    nolog = config['nolog']

    if nolog:
        log_file = '/dev/null'
    else:
        log_file = config['log_file']

    lvls = {'CRITICAL': 50,
            'ERROR': 40,
            'WARNING': 30,
            'WARN': 30,
            'INFO': 20,
            'DEBUG': 10,
            'NOTSET': 0}

    lvl = lvls[level]

    if level == 'DEBUG':
        logformat = '[%(asctime)s] [%(threadName)s] [%(levelname)s]' +\
            ' [%(module)s] [%(lineno)d] [%(name)s] : %(message)s'

    else:
        logformat = '[%(asctime)s] [%(levelname)s] : %(message)s'

    formatter = logging.Formatter(logformat)

    try:
        logging.basicConfig(
            filename=log_file,
            level=lvl,
            format=logformat, disable_existing_loggers=False)

        if foreground is True:
            logger.setLevel(lvl)
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(formatter)
            streamHandler.setLevel(lvl)
            logger.addHandler(streamHandler)

    except Exception as e:
        logger.error(e, exc_info=True)
