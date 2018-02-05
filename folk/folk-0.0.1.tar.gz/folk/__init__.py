"""Utilities for pandas."""

from .model import ParameterizedModel
from .pipe import ParameterizedPipeline

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
del _version

for name in ['get_versions', '_version', 'model', 'pipe', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass
