# coding=utf-8
"""
Dummy
"""

import sys
import elib
from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__: str = get_distribution('pvnhxgmgiq').version
except DistributionNotFound:  # pragma: no cover
    if getattr(sys, 'frozen', False):
        __version__: str = elib.exe_version.get_product_version(sys.executable).file_version
    else:
        # package is not installed
        __version__: str = 'not installed'
