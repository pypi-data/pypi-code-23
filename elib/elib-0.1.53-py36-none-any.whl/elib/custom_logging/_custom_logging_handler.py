# coding=utf-8
"""
Install a handler to redirect all INFO messages (and higher) to the Discord Channel
"""
import abc
import logging as base

from ._constants import LOGGERS


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
        LOGGERS[logger.name][self.name] = self
        logger.addHandler(self)
