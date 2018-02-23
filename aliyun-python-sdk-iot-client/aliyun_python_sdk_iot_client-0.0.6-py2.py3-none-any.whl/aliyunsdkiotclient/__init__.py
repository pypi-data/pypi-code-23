# -*- coding: utf-8 -*-

# Set default logging handler to avoid "No handler found" warnings.
import logging
import warnings

from .exceptions import (
	FileModeWarning
)

try:  # Python 2.7+
	from logging import NullHandler
except ImportError:
	class NullHandler(logging.Handler):
		def emit(self, record):
			pass

logging.getLogger(__name__).addHandler(NullHandler())

# FileModeWarnings go off per the default.
warnings.simplefilter('default', FileModeWarning, append=True)
