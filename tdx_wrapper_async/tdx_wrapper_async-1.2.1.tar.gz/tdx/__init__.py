import os

TDX_ROOT = os.path.dirname(os.path.abspath(__file__))
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
