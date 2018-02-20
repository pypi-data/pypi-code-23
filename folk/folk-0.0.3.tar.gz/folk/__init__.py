"""Utilities for pandas."""

from .model import (  # noqa: F401
    ParameterizedModel,
    ConstrainedParameterizedModel,
)
from .pipe import ParameterizedPipeline  # noqa: F401

from ._version import get_versions
__version__ = get_versions()['version']

for name in ['get_versions', '_version', 'model', 'pipe', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass
