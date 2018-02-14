# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import time
import unittest
from functools import partial
from curtsies.formatstring import (FmtStr, fmtstr, Chunk, linesplit,
                                   normalize_slice, width_aware_slice)
from curtsies.fmtfuncs import *
from curtsies.termformatconstants import FG_COLORS
from curtsies.formatstringarray import fsarray, FSArray, FormatStringTest

try:
    from unittest import skip
except ImportError:
    def skip(f):
        return lambda self: None

PY2 = sys.version_info[0] == 2

try:
    unicode = unicode
except:
    unicode = str


def timeit(func, n=3):
    """Wall-time a function"""
    times = []
    for i in range(n):
        t0 = time.time()
        func()
        dt = time.time() - t0
        times.append(dt)
    return sorted(times)[n // 2]  # take the median (taking faster time if there's a tie)


class TestWidthAwareSlice(unittest.TestCase):
    """Who knows how flaky this will be."""

    def test_width_aware_slice_is_not_quadratic(self):
        """Once it was and there was much sadness, bpython #702"""
        def slice_one_char(n):
            fmtstr('a'*n).width_aware_slice(slice(0, 1, None))

        t_1000 = timeit(partial(slice_one_char, 1000))
        t_2000 = timeit(partial(slice_one_char, 2000))
        assert t_2000 < t_1000 * 3
