### Import MySportsFeeds class(es) upon initiation of the program
from .MySportsFeeds_API import MySportsFeeds
from .v1_0 import API_v1_0

from pkg_resources import get_distribution

__version__ = "1.0.0" #get_distribution('ohmysportsfeedspy').version