"""Combiner functions for pandas.Series input."""
from __future__ import print_function, absolute_import, division

import numpy as np
import pandas as pd


def first_of(elems):
    """Return the first element of the input."""
    return elems.iat[0]


def lastof(elems):
    """Return the last element of the input."""
    return elems.iat[-1]


def join_strings(ser):
    """Join a Series of strings by commas."""
    # TODO if ser elements are also comma-separated, split+uniq those too
    return ','.join(ser.unique())


def merge_strands(ser):
    strands = ser.drop_duplicates()
    if len(strands) > 1:
        return '.'
    return strands.iat[0]
