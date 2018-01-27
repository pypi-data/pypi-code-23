# -*- coding: utf-8 -*-
"""
Mattophobia String Generator
~~~~~~~~~~~~~~~~~~~
Generates a string that Mattophobia would probably say.
:copyright: (c) 2018 DerpyChap
:license: MIT, see LICENSE for more details.
"""

__title__ = 'mattophobia_says'
__author__ = 'DerpyChap'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018 DerpyChap'
__version__ = '0.1.0'

from collections import namedtuple
from .mattsays import MattSays

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(
    major=0, minor=1, micro=0, releaselevel='final', serial=0)
