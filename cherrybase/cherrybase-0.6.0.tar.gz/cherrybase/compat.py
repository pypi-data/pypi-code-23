# -*- coding: utf-8 -*-

import sys


PY3 = sys.version_info.major >= 3


if PY3:
    unicode = str
else:
    unicode = unicode
