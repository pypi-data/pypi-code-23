import logging
from logging.config import dictConfig


def create_logger(name='', base_path='', debug_filename='debug.log', info_filename='info.log'):

    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)

    logging_config = dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            'f': {'format': '%(asctime)s - %(name)-12s %(levelname)-8s %(message)s'}
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "f",
                "stream": "ext://sys.stdout"
            },

            "debug_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "f",
                "filename": base_path + debug_filename,
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8"
            },

            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "f",
                "filename": base_path + info_filename,
                "maxBytes": 10485760,
                "backupCount": 10,
                "encoding": "utf8"
            },
        },
        root={
            "level": "DEBUG",
            "handlers": ["console", "debug_file_handler", "info_file_handler"]
        }
    )

    dictConfig(logging_config)
    logger = logging.getLogger(name)
    return logger


def test():
    logger = create_logger(name='test')
    logger.debug('test')
    logger.error('error test')