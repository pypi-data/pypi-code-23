# coding=utf-8
"""
Convenience functions to manage logging
"""

import logging as base
import logging.handlers as base_handlers
import sys
from pathlib import Path

from elib import LOGGER as ELIB_LOGGER
from . import _constants


# noinspection SpellCheckingInspection


def set_handler_level(logger_name, handler_name, level):
    """
    Sets output level for console handlers

    Args:
        logger_name: name of the logger to update
        level: desired level
    """
    if isinstance(level, str):
        level = _constants.LEVELS[level.upper()]
    _constants.LOGGERS[logger_name][handler_name].setLevel(level)


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
        log_to_file: bool = False,
        rotate_logs: bool = False,
        rotate_log_when: str = 'midnight',
        rotate_log_backup_count: int = 7,
        console_level=base.ERROR,
        file_level=base.DEBUG,
        console_format=_constants.DEFAULT_CONSOLE_FORMAT,
        file_format=_constants.DEFAULT_FILE_FORMAT,
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
    if logger_name in _constants.LOGGERS:
        _constants.LOGGERS[logger_name]['logger'].debug(f'logger already initialized: {logger_name}')
        return _constants.LOGGERS[logger_name]['logger']

    kwargs = locals()

    if _constants.ROOT_LOGGER is None:
        logger = base.getLogger(logger_name)
        _constants.ROOT_LOGGER = logger
    else:
        logger = _constants.ROOT_LOGGER.getChild(logger_name)

    logger.setLevel(base.DEBUG)

    console_handler = base.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(base.Formatter(console_format))

    logger.addHandler(console_handler)
    logger.debug('added console logging handler')

    _constants.LOGGERS[logger.name] = {
        'logger': logger,
        'ch': console_handler,
    }

    if log_to_file:
        file_handler = _setup_file_logging(logger, **kwargs)
        _constants.LOGGERS[logger.name]['fh'] = file_handler

    return logger


def activate_elib_logging():
    """
    Attaches all handlers of the root logger to the ELIB logger
    """
    for handler in _constants.ROOT_LOGGER.handlers:
        ELIB_LOGGER.addHandler(handler)
