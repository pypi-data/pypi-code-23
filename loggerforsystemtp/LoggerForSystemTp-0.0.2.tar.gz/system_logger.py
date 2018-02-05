import logging
import logging.config
import os


class Logger:

    def env_var(key, default=None):
        val = os.environ.get(key, default)

        bool_dict = {'True': True, 'False': False}
        return bool_dict[val] if val in bool_dict else val

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(asctime)s %(message)s'
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
            }
        },
        'loggers': {
            'basic': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            }
        },
    }

    def __init__(self, name):
        logging.config.dictConfig(self.LOGGING)
        self.logger = logging.getLogger(name)

