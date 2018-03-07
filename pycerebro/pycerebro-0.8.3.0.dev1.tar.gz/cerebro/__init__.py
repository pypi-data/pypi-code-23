# Copyright CerebroData Inc.

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Import the public API
from cerebro.cdas import context, version
