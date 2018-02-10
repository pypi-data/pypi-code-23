# coding=utf-8
"""
Convenience functions to manage logging
"""

import logging as base
import logging.handlers as base_handlers
import sys

# noinspection SpellCheckingInspection
DEFAULT_FORMAT = '%(asctime)s %(levelname)8s %(name)s[%(lineno)d].%(funcName)s: %(message)s'
_LOGGERS = {}


# pylint: disable=too-many-arguments
def _setup_file_logging(logger,
                        log_to_file: str,
                        rotate_logs: bool,
                        rotate_log_when: str,
                        rotate_log_backup_count: int,
                        file_level,
                        file_format,
                        **_):
    if rotate_logs:
        file_handler = base_handlers.TimedRotatingFileHandler(
            filename=log_to_file,
            when=rotate_log_when,
            backupCount=rotate_log_backup_count,
            encoding='utf8',
        )
    else:
        file_handler = base.FileHandler(
            filename=log_to_file,
            encoding='utf8'
        )

    file_handler.setLevel(file_level)
    file_handler.setFormatter(base.Formatter(file_format))

    logger.addHandler(file_handler)
    if rotate_logs:
        logger.debug(f'added rotating file logging handler: {log_to_file}')
    else:
        logger.debug(f'added file logging handler: {log_to_file}')


# pylint: disable= unused-argument
def get_logger(
        logger_name: str,
        log_to_file: str = None,
        rotate_logs: bool = False,
        rotate_log_when: str = 'midnight',
        rotate_log_backup_count: int = 7,
        console_level=base.DEBUG,
        file_level=base.DEBUG,
        console_format=DEFAULT_FORMAT,
        file_format=DEFAULT_FORMAT,
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
        _LOGGERS[logger_name].warning(f'logger already initialized: {logger_name}')
        return _LOGGERS[logger_name]

    kwargs = locals()
    logger = base.getLogger(logger_name)
    logger.setLevel(base.DEBUG)

    if log_to_file:
        _setup_file_logging(logger, **kwargs)

    console_handler = base.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(base.Formatter(console_format))

    logger.addHandler(console_handler)
    logger.debug('added console logging handler')

    _LOGGERS[logger_name] = logger

    return logger
