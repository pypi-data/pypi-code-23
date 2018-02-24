# coding=utf-8
"""
Placeholder for future personal library
"""

from pkg_resources import DistributionNotFound, get_distribution

# noinspection PyUnresolvedReferences
from . import config, console, custom_logging, custom_random, downloader, exe_version, hash_, paste, path, pretty, \
    run, settings, tts

try:
    __version__ = get_distribution('elib').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'
