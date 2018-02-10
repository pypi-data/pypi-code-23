# coding=utf-8
"""
Manages custom logging handlers
"""

import abc
import logging as base


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

    def register(self, main_logger: base.Logger):
        """
        Registers the handler with an existing logger

        :param main_logger: logger to attach to
        """
        main_logger.debug(f'registering logging handler: {self.name}')
        main_logger.addHandler(self)
