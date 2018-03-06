# -*- coding: utf-8 -*-
from .exceptions import *
from .main import *
from .completezip import *
from .validate import *

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
