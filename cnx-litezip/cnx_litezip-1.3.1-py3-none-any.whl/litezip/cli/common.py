# -*- coding: utf-8 -*-
from litezip.logger import configure_logging


console_logging_config = {
    'version': 1,
    'formatters': {
        'cli': {
            'format': '%(levelname)-5.5s: %(message)s',
        },
    },
    'filters': {},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'cli',
            'filters': [],
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'litezip': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': 0,
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': [],
    },
}


def set_verbosity(verbose):
    config = console_logging_config.copy()
    if verbose is None:
        config['loggers']['litezip']['level'] = 'ERROR'
    elif verbose:
        config['loggers']['litezip']['level'] = 'DEBUG'
    else:  # quiet
        config['loggers']['litezip']['level'] = 100
    configure_logging(config)
