import sys
import logging

from colorama import init

from .formatter import DateTimeFormatter
from .stream import ColoredStreamHandler
from .settings import LOGORAMA_DEFAULT_LEVEL, LOGORAMA_DISABLE_COLORS, \
    LOGORAMA_DEFAULT_FORMAT


log_formatter = DateTimeFormatter(LOGORAMA_DEFAULT_FORMAT)

log_formatter.default_msec_format = "%s.%03d"
if LOGORAMA_DISABLE_COLORS:
    ch = logging.StreamHandler(sys.stdout)
else:
    ch = ColoredStreamHandler()
ch.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(ch)
logger.setLevel(logging.INFO)

init(autoreset=True)


class BaseLogger(object):
    LOG_LEVEL = LOGORAMA_DEFAULT_LEVEL

    @property
    def logger(self):
        rv = logging.getLogger(
            name=self.__class__.__module__ + "." + self.__class__.__name__)
        rv.setLevel(self.LOG_LEVEL)
        return rv
