"""
Placeholder for future personal library
"""
from pkg_resources import DistributionNotFound, get_distribution

from . import config, console, custom_logging, custom_random, paste, path, tts

try:
    __version__ = get_distribution('elib').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

MAIN_LOGGER = custom_logging.get_logger('ELIB')
MAIN_LOGGER.info(f'ELIB version {__version__}')
