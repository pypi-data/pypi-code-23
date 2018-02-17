""" fslutils package
"""

from .fsf import FSF
from . import fsf

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
