"""
Override logging base functions
"""


import inspect
import logging


def _get_logger_parent(name=None):
    if name is None:
        curframe = inspect.currentframe()
        frame = inspect.getouterframes(curframe)[2].frame
        logger_name = frame.f_globals['__name__'].split('.')[0]
    else:
        logger_name = name
    return logging.getLogger(logger_name)


def _get_logger(name=None):
    if name is None:
        curframe = inspect.currentframe()
        frame = inspect.getouterframes(curframe)[2].frame
        # print('>>>', inspect.getframeinfo(frame))
        # print('<<<', frame.f_globals['__name__'])
        logger_name = frame.f_globals['__name__']
    else:
        logger_name = name
    return logging.getLogger(logger_name)


def critical(msg, *args, _name=None, **kwargs):
    logger = _get_logger(_name)
    logger.critical(msg, *args, **kwargs)


def error(msg, *args, _name=None, **kwargs):
    logger = _get_logger(_name)
    logger.error(msg, *args, **kwargs)


def exception(msg, *args, exc_info=True, _name=None, **kwargs):
    error(msg, *args, exc_info=exc_info, **kwargs)


def warning(msg, *args, _name=None, **kwargs):
    logger = _get_logger(_name)
    logger.warning(msg, *args, **kwargs)


def info(msg, *args, _name=None, **kwargs):
    logger = _get_logger(_name)
    logger.info(msg, *args, **kwargs)


def debug(msg, *args, _name=None, **kwargs):
    logger = _get_logger(_name)
    logger.debug(msg, *args, **kwargs)

