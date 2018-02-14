# coding=utf-8
"""
Convenience functions to manage logging
"""

import abc
import logging as base
import logging.handlers as base_handlers
import sys
from pathlib import Path

# noinspection SpellCheckingInspection
DEFAULT_CONSOLE_FORMAT = '%(relativeCreated)08d ms ' \
                         '%(levelname)8s ' \
                         '%(name)s ' \
                         '%(message)s'

DEFAULT_FILE_FORMAT = '%(asctime)s %(levelname)8s %(name)s ' \
                      '%(process)d %(processName)s ' \
                      '%(thread)d %(threadName)s ' \
                      '%(pathname)s[%(lineno)d].%(funcName)s: ' \
                      '%(message)s'
_LOGGERS = {}

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


class CustomLoggingHandler(base.Handler):
    """
    Install a handler to redirect all INFO messages (and higher) to the Discord Channel
    """

    def __init__(self, name: str, level=base.INFO):
        """
        Creates a logging Handler
        :param name: name of this handler
        :param level: instance of logging.* level
        """
        base.Handler.__init__(self, level)
        self.set_name(name)

    @abc.abstractmethod
    def emit(self, record: base.LogRecord):
        """
        Redirects the record to the Discord channel if its level is INFO or higher

        Args:
            record: logging.record to emit
        """

    def register(self, logger: base.Logger):
        """
        Registers the handler with an existing logger

        :param logger: logger to attach to
        """
        logger.debug(f'registering logging handler: {self.name}')
        _LOGGERS[logger.name][self.name] = self
        logger.addHandler(self)


def set_handler_level(logger_name, handler_name, level):
    """
    Sets output level for console handlers

    Args:
        logger_name: name of the logger to update
        level: desired level
    """
    if isinstance(level, str):
        level = LEVELS[level.upper()]
    _LOGGERS[logger_name][handler_name].setLevel(level)


# pylint: disable=too-many-arguments
def _setup_file_logging(logger: base.Logger,
                        logger_name: str,
                        rotate_logs: bool,
                        rotate_log_when: str,
                        rotate_log_backup_count: int,
                        file_level,
                        file_format,
                        **_):
    file_name = Path(f'{logger_name}.log').absolute()
    if rotate_logs:
        file_handler = base_handlers.TimedRotatingFileHandler(
            filename=file_name,
            when=rotate_log_when,
            backupCount=rotate_log_backup_count,
            encoding='utf8',
        )
    else:
        if Path(file_name).exists():
            Path(file_name).unlink()
        file_handler = base.FileHandler(
            filename=file_name,
            encoding='utf8'
        )

    file_handler.setLevel(file_level)
    file_handler.setFormatter(base.Formatter(file_format))

    logger.addHandler(file_handler)
    if rotate_logs:
        logger.debug(f'added rotating file logging handler: {file_name}')
    else:
        logger.debug(f'added file logging handler: {file_name}')

    return file_handler


# pylint: disable= unused-argument
def get_logger(
        logger_name: str,
        log_to_file: bool = True,
        rotate_logs: bool = False,
        rotate_log_when: str = 'midnight',
        rotate_log_backup_count: int = 7,
        console_level=base.DEBUG,
        file_level=base.DEBUG,
        console_format=DEFAULT_CONSOLE_FORMAT,
        file_format=DEFAULT_FILE_FORMAT,
) -> base.Logger:
    """
    Set up the logger

    :param logger_name: name of the logger
    :param log_to_file: path to log file [optional]
    :param rotate_logs: whether or not to rotate the log
    :param rotate_log_when: when log rotation should occur
    :param rotate_log_backup_count: number of log files to keep
    :param console_level: level for console logging
    :param file_level: level for file logging
    :param console_format: console formatter string
    :param file_format: file formatter string

    :return: logger object
    """
    if logger_name in _LOGGERS:
        _LOGGERS[logger_name]['logger'].warning(f'logger already initialized: {logger_name}')
        return _LOGGERS[logger_name]['logger']

    kwargs = locals()
    logger = base.getLogger(logger_name)
    logger.setLevel(base.DEBUG)

    console_handler = base.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(base.Formatter(console_format))

    logger.addHandler(console_handler)
    logger.debug('added console logging handler')

    _LOGGERS[logger_name] = {
        'logger': logger,
        'ch': console_handler,
    }

    if log_to_file:
        file_handler = _setup_file_logging(logger, **kwargs)
        _LOGGERS[logger_name]['fh'] = file_handler

    return logger
