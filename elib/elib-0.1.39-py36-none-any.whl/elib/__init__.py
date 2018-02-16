"""
Placeholder for future personal library
"""
from pkg_resources import DistributionNotFound, get_distribution

from . import config, console, custom_logging, custom_random, paste, path, tts, settings
from ._run import run
from .pretty import pretty_format

try:
    __version__ = get_distribution('elib').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

if __package__ == 'elib':  # pragma: no cover
    LOGGER = custom_logging.get_logger('ELIB')
    LOGGER.info(f'ELIB version {__version__}')
