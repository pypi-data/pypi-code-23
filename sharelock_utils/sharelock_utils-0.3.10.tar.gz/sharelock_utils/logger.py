import logging
from logging.config import dictConfig

import os


def create_logger(name='', debug_filename='debug.log', info_filename='info.log', num_backups=5):

    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)

    base_file_path = os.environ.get('LOGS_BASE_PATH', '')
    syslog_path = os.environ.get('SYSLOG_PATH', None)

    handlers = {
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
                "filename": base_file_path + debug_filename,
                "maxBytes": 10485760,
                "backupCount": num_backups,
                "encoding": "utf8"
            },

            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "f",
                "filename": base_file_path + info_filename,
                "maxBytes": 10485760,
                "backupCount": num_backups,
                "encoding": "utf8"
            },
            'syslog': {
                'level': os.environ.get('SYSLOG_LEVEL', 'INFO'),
                'class': 'logging.handlers.SysLogHandler',
                'formatter': 'f',
                'facility': 'local1',
                'address': syslog_path,
            },
        }

    if not syslog_path:
        del handlers['syslog']

    loggers = {
            "elasticsearch": {
                "level": "WARNING",
                "propagate": "no"
            },
            "urllib3": {
                "level": "WARNING",
                "propagate": "no"
            },
            "tweepy": {
                "level": "WARNING",
                "propagate": "no"
            },
            "prawcore": {
                "level": "WARNING",
                "propagate": "no"
            }
        }

    root_hanlders = ["console", "debug_file_handler", "info_file_handler",]
    if syslog_path:
      root_hanlders.append("syslog")
    logging_config = dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            'f': {'format': '%(asctime)s - %(name)-12s %(levelname)-8s %(message)s'},
            'syslog_f': {}
        },
        handlers=handlers,
        loggers=loggers,
        root={
            "level": "DEBUG",
            "handlers": root_hanlders
        }
    )

    dictConfig(logging_config)
    logger = logging.getLogger(name)
    return logger


def test():
    logger = create_logger(name='test')
    logger.debug('test')
    logger.error('error test')
