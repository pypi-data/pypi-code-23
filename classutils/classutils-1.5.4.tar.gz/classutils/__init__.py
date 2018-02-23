# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
from .decorators import deprecated, class_cache_result, clear_class_cached_results
from .decorators import profiling
from .observer import Observable, ObserverMixIn, ObserverError
from .singleton import SingletonType

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
