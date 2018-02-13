# coding=utf-8
"""
Tests logging package
"""

import logging
import logging.handlers
from pathlib import Path

import pytest

import elib


@pytest.fixture(scope='function')
def setup_logging(caplog):
    """Provides a logger and the caplog fixture"""
    logger = elib.custom_logging.get_logger(logger_name='TEST_LOGGER', console_level=logging.DEBUG)
    yield logger, caplog


# noinspection PyShadowingNames
def test_logger(setup_logging):
    logger, caplog = setup_logging
    assert isinstance(logger, logging.Logger)
    assert logger is logging.getLogger(logger.name)
    caplog.set_level(logging.DEBUG)
    logger.info('test_message_debug')
    assert 'test_message_debug' in caplog.text
    assert elib.custom_logging.get_logger(logger.name) is logging.getLogger(logger.name)


# noinspection PyShadowingNames
def test_double_instantiation():
    first_logger = elib.custom_logging.get_logger('test_logger')
    second_logger = elib.custom_logging.get_logger('test_logger')
    assert first_logger is second_logger


# noinspection PyShadowingNames
@pytest.mark.parametrize('levels', [
    (logging.DEBUG, logging.INFO, 'debug'),
    (logging.INFO, logging.WARNING, 'info'),
    (logging.WARNING, logging.ERROR, 'warning'),
    (logging.ERROR, logging.CRITICAL, 'error'),
])
def test_logger_levels(setup_logging, levels):
    logger, caplog = setup_logging
    caplog.set_level(levels[1], logger='TEST_LOGGER')
    out_func = getattr(logger, levels[2])
    out_func('test_message_debug')
    assert 'test_message_debug' not in caplog.text
    caplog.set_level(levels[0], logger='TEST_LOGGER')
    out_func('test_message_debug')
    assert 'test_message_debug' in caplog.text


# noinspection PyShadowingNames
@pytest.mark.parametrize('level', ['debug', 'info', 'warning', 'error', 'critical'])
def test_logger_not_set(setup_logging, level):
    logger, caplog = setup_logging
    caplog.set_level(logging.NOTSET)
    out_func = getattr(logger, level)
    out_func('test_message_debug')
    assert 'test_message_debug' in caplog.text


def test_file_handler():
    log_file = Path('./log.file')
    assert not log_file.exists()
    logger = elib.custom_logging.get_logger(elib.custom_random.random_string(), log_to_file=str(log_file))
    logger.warning('test')
    assert log_file.exists()
    assert 'test' in log_file.read_text()


def test_file_handler_levels():
    log_file = Path('./log.file')
    assert not log_file.exists()
    logger = elib.custom_logging.get_logger(elib.custom_random.random_string(),
                                            log_to_file=str(log_file), file_level=logging.ERROR)
    logger.warning('test')
    assert log_file.exists()
    assert 'test' not in log_file.read_text()


def test_rotating_file_handler():
    log_file = Path('./log.file', )
    assert not log_file.exists()
    logger = elib.custom_logging.get_logger(elib.custom_random.random_string(),
                                            log_to_file=str(log_file), rotate_logs=True)
    logger.warning('test')
    assert log_file.exists()
    assert 'test' in log_file.read_text()
    assert len(list(log_file.parent.glob('*'))) == 1
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            handler.doRollover()
            assert len(list(log_file.parent.glob('*'))) == 2
            break
    else:
        assert logger.handlers is None
        raise LookupError('no rotating file handler found')


# noinspection PyShadowingNames
def test_custom_handler(setup_logging):
    logger, _ = setup_logging

    result = False

    def _callback(*_):
        nonlocal result
        result = True

    handler = elib.custom_logging.CustomLoggingHandler('handler')
    handler.emit = _callback

    handler.register(logger)

    logger.info('test')
    assert result


@pytest.mark.parametrize(
    'level',
    [logging.DEBUG, logging.INFO, logging.ERROR, logging.WARN, logging.CRITICAL]
)
def test_console_handler_level(level):
    logger = elib.custom_logging.get_logger(elib.custom_random.random_string(4))
    elib.custom_logging.set_handler_level(logger.name, 'ch', level)

    for handler in logger.handlers:
        assert handler.level is level

    handler = elib.custom_logging.CustomLoggingHandler('handler')
    handler.register(logger)

    elib.custom_logging.set_handler_level(logger.name, 'handler', level)

    for handler in logger.handlers:
        assert handler.level is level


def test_console_handler_levelas_string():
    logger = elib.custom_logging.get_logger(elib.custom_random.random_string(4))

    elib.custom_logging.set_handler_level(logger.name, 'ch', 'critical')
    for handler in logger.handlers:
        assert handler.level is logging.CRITICAL

    elib.custom_logging.set_handler_level(logger.name, 'ch', 'debug')
    for handler in logger.handlers:
        assert handler.level is logging.DEBUG

    elib.custom_logging.set_handler_level(logger.name, 'ch', 'WaRN')
    for handler in logger.handlers:
        assert handler.level is logging.WARN

    elib.custom_logging.set_handler_level(logger.name, 'ch', 'err')
    for handler in logger.handlers:
        assert handler.level is logging.ERROR
