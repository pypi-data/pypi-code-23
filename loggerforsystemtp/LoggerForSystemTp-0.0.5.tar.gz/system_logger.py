import logging
import logging.config
import os
import sys

class Logger:

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def env_var(self, key, default=None):
        val = os.environ.get(key, default)

        bool_dict = {'True': True, 'False': False}
        return bool_dict[val] if val in bool_dict else val

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s  \t %(asctime)s  \t%(module)s \t%(process)d \t%(thread)d \t%(message)s'
            },
            'simple': {
                'format': '%(levelname)s  \t %(asctime)s  \t%(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1024 * 1024 * 10,  # 10MB
                'backupCount': 10,
                'filename': os.path.abspath('logs/basic.log'),
                'formatter': env_var('FORMAT','simple'),
                'encoding': 'utf-8'
            },
            'test_log': {
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1024 * 1024 * 10,  # 10MB
                'backupCount': 10,
                'filename': os.path.abspath('logs/test_log.log'),
                'formatter': env_var('FORMAT', 'simple'),
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'basic': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            },
            'test_log': {
                'handlers': ['console', 'test_log'],
                'level': 'DEBUG',
            }
        },
    }

    def __init__(self, name):
        if not os.path.exists(os.path.abspath('logs')):
            os.makedirs(os.path.abspath('logs'))

        sys.excepthook = self.handle_exception
        logging.config.dictConfig(self.LOGGING)
        self.logger = logging.getLogger(name)

