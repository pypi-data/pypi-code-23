# coding=utf-8
"""
Logging constants
"""
import logging as base

DEFAULT_CONSOLE_FORMAT = '%(relativeCreated)08d ms ' \
                         '%(levelname)8s ' \
                         '%(name)s ' \
                         '%(message)s'
DEFAULT_FILE_FORMAT = '%(asctime)s %(levelname)8s %(name)s ' \
                      '%(process)d %(processName)s ' \
                      '%(thread)d %(threadName)s ' \
                      '%(pathname)s[%(lineno)d].%(funcName)s: ' \
                      '%(message)s'
LOGGERS = {}
ROOT_LOGGER = None
LEVELS = {
    'DEBUG': base.DEBUG,
    'INFO': base.INFO,
    'WARNING': base.WARN,
    'WARN': base.WARN,
    'ERROR': base.ERROR,
    'ERR': base.ERROR,
    'CRITICAL': base.CRITICAL,
    'CRIT': base.CRITICAL,
}
