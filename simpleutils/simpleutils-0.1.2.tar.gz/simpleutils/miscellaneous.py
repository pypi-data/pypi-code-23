# -*- coding: utf-8 -*-
"""
Created on 2017-5-7

@author: cheng.li
"""

import sys
import os
import datetime as dt


def add_parent_path(name, level):
    current_path = os.path.abspath(name)
    sys.path.append(os.path.sep.join(current_path.split(os.path.sep)[:-level]))


def to_datetime(date):
    if isinstance(date, dt.datetime):
        return dt.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
    else:
        return dt.datetime(date.year, date.month, date.day)


def list_eq(lhs, rhs):

    if not lhs and not rhs:
        return True

    if len(lhs) != len(rhs):
        return False

    for i, v1 in enumerate(lhs):
        if v1 != rhs[i]:
            return False
    return True
