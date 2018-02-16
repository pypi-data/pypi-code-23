"""
Placeholder for future personal library
"""
import logging

from pkg_resources import DistributionNotFound, get_distribution

LOGGER = logging.getLogger('ELIB')
LOGGER.addHandler(logging.NullHandler())

# pylint: disable=wrong-import-position
from . import config, console, custom_logging, custom_random, downloader, hash_, paste, path, settings, tts
# pylint: disable=wrong-import-position
from ._run import run
# pylint: disable=wrong-import-position
from .pretty import pretty_format

try:
    __version__ = get_distribution('elib').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'
