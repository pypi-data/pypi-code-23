# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
from ._dtparse import DatetimeUtils

__all__ = ['parse', 'parse_regex', 'parse_py', 'parse_chrono']


def parse_py(dt_string):
    return datetime(int(dt_string[0:4]), int(dt_string[5:7]), int(dt_string[8:10]))


_utils = DatetimeUtils(datetime)
parse = _utils.parse
parse_regex = _utils.parse_regex
parse_chrono = _utils.parse_chrono
