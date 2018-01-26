# -*- coding: utf-8 -*-

"""
The :mod:`pipesnake` is yet another pandas sklearn-inspired pipeline data processor.
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging

from pipesnake import metadata

__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
