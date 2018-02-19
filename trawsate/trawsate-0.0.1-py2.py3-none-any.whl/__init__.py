# -*- coding: utf-8 -*-
from typing import Any
from pkg_resources import get_distribution, DistributionNotFound
import os

AccessKeyPair = Any

from trawsate.rotator import Rotator
from trawsate.parallel import JobResult, rotate_keys
from trawsate.single import AccessKeyStateError, rotate_key
from trawsate.travis import TravisError

__title__ = 'trawsate'
__description__ = 'Rotates AWS access keys used by Travis CI.'
__author__ = 'George Brighton'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018 George Brighton'


# adapted from http://stackoverflow.com/a/17638236
try:
    dist = get_distribution(__title__)
    path = os.path.normcase(dist.location)
    pwd = os.path.normcase(__file__)
    if not pwd.startswith(os.path.join(path, __title__)):
        raise DistributionNotFound()
    __version__ = dist.version
except DistributionNotFound:
    __version__ = 'unknown'
