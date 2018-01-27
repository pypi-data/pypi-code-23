# -*- coding: utf-8 -*-
import logging
import logging.config
from logging.config import dictConfig

log = logging.getLogger(__name__)

# maybe this should go in settings

DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sqlwriter': {
            'format': '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'sqlwriter',
            'stream': 'ext://sys.stdout'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    }
}


def configure_logging():
    assert (isinstance(DEFAULT_LOGGING_CONFIG, dict))
    try:
        # Try to init logging
        dictConfig(DEFAULT_LOGGING_CONFIG)
    except ValueError as e:
        log.warning('Unable to load the config, contains a configuration error.')
        raise e
    return DEFAULT_LOGGING_CONFIG


configure_logging()


class LoggingMixin(object):
    _logger_configured = False

    @property
    def logger(self):
        if not self._logger_configured:
            logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
            self._logger_configured = True
        name = '.'.join([self.__class__.__name__])
        return logging.getLogger(name)
