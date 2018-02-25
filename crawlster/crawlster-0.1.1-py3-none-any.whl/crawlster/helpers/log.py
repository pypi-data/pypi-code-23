import logging

import colorlog
import sys

from crawlster.config import ChoiceOption
from crawlster.helpers.base import BaseHelper


class LoggingHelper(BaseHelper):
    """Logging helper that handles all the crawling logging.

    Must provide the following methods:

    - initialize() (inherited from BaseHelper)
    - ``debug(*args, **kwargs)`` compatible with the :py:mod:`logging`
       interface
    - same for ``info``, ``warning``, ``error`` and ``critical``

    """
    name = 'log'
    valid_log_levels = ('debug', 'info', 'warning', 'error', 'critical')
    config_options = {
        'log.level': ChoiceOption(valid_log_levels, default='info')
    }

    DEFAULT_FORMAT = "%(log_color)s%(levelname)s - %(name)s - %(message)s"

    def __init__(self):
        super(LoggingHelper, self).__init__()
        self.logger = None

    def initialize(self):
        """Creates and initializes the logger"""
        level = self.parse_level(self.config.get('log.level'))

        logger = logging.getLogger('crawlster')
        stream_handler = self.make_stream_handler(level)
        logger.addHandler(stream_handler)
        logger.setLevel(level)
        self.logger = logger

    def make_stream_handler(self, level):
        """Creates a colored stream handler that writes to STDOUT"""
        colored_formatter = colorlog.ColoredFormatter(self.DEFAULT_FORMAT)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(colored_formatter)
        stream_handler.setLevel(level)
        return stream_handler

    def __getattr__(self, item):
        """Delegates method calls to the wrapped logger"""
        if item not in ('debug', 'info', 'warning', 'error', 'critical'):
            raise AttributeError()
        return getattr(self.logger, item)

    def parse_level(self, level_name):
        """Converts human readable level name to logging constants"""
        return getattr(logging, level_name.upper())
