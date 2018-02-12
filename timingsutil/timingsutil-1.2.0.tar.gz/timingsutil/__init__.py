# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
from .timers import Timeout, Stopwatch, Throttle

ONE_MINUTE = 60
FIVE_MINUTES = ONE_MINUTE * 5
ONE_HOUR = ONE_MINUTE * 60
THIRTY_MINUTES = ONE_MINUTE * 30
EIGHT_HOURS = ONE_HOUR * 8

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
