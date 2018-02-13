import copy
import logging
from logging import config as loggingconfig

from bglogs.logger import _get_logger_parent
from bglogs.utils import override_dict


BGCONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'bgfmt': {
            '()': 'bglogs.format.BGFmt'
        },
        'full': {
            '()': 'bglogs.format.FullFmt'
        },
        'basic': {
            '()': 'bglogs.format.BasicFmt'
        }
    },
    'filters': {
        'info': {
            '()': 'bglogs.filter.InfoFilter'
        }
    },
    'handlers': {
        'bgout': {
            'class': 'logging.StreamHandler',
            'formatter': 'bgfmt',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
            'filters': ['info']
        },
        'bgerr': {
            'class': 'logging.StreamHandler',
            'formatter': 'bgfmt',
            'level': 'WARNING',
            'stream': 'ext://sys.stderr',
        },
        # 'bgfile': {
        #     'class': 'logging.FileHandler',
        #     'formatter': 'bgfmt',
        #     'filename': 'log.txt',
        #     'mode': 'w'  # ensure that it is created for each run
        # }
    },
    'loggers': {},
    'root': {
        'level': 'WARNING',
        'handlers': ['bgout', 'bgerr']
    }
}


def configure_as_library(_name=None):
    """
    Configure a package as a library
    adding a NullHandler
    """
    logger = _get_logger_parent(_name)
    logger.addHandler(logging.NullHandler())


def configure(_name=None, debug=False, conf=None):
    """
    Configure the logger for a normal application

    Args:
        _name (str, optional): name of the logger to be configured.
          If not passed the parent logger of the caller is used.
        debug (bool, optional): level for the main logger (DEBUG or INFO)
        conf (dict, optional): optional extra configuration
          for the logging module

    """
    logger = _get_logger_parent(_name)
    if conf is None:
        conf = BGCONF
    else:
        default_conf = copy.deepcopy(BGCONF)
        override_dict(default_conf, conf)
        conf = default_conf
    conf['loggers'][logger.name] = {
        'level': logging.DEBUG if debug else logging.INFO
    }
    loggingconfig.dictConfig(conf)
