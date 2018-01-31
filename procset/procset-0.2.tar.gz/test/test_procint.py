# -*- coding: utf-8 -*-

# Copyright © 2017, 2018
# Contributed by Raphaël Bleuse <raphael.bleuse@imag.fr>
#
# This file is part of procset.py, a pure python module to manage sets of
# closed intervals.
#
#   procset.py is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License version 3 only
#   as published by the Free Software Foundation.
#
#   procset.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License version 3 for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License version 3 along with this program.  If not, see
#   <https://www.gnu.org/licenses/>.

import copy
import pytest
from procset import ProcInt


# pylint: disable=no-self-use,too-many-public-methods
class TestNew:
    def test_point(self):
        itv = ProcInt(0, 0)
        assert itv == (0, 0)
        assert len(itv) == 1
        assert 0 in itv

    def test_wide(self):
        itv = ProcInt(0, 41)
        assert itv == (0, 41)
        assert len(itv) == 42
        for point in range(0, 42):
            assert point in itv

    def test_reversed_args(self):
        itv = ProcInt(sup=41, inf=0)  # notice reversed arguments
        assert itv == (0, 41)
        assert len(itv) == 42
        for point in range(0, 42):
            assert point in itv

    def test_enforce_nonnegative(self):
        with pytest.raises(ValueError, match='^Invalid negative bound\(s\)$'):
            ProcInt(-1, 0)
        with pytest.raises(ValueError, match='^Invalid negative bound\(s\)$'):
            ProcInt(-15, -1)

    def test_bad_type_inf(self):
        with pytest.raises(TypeError, match='^ProcInt\(\) argument inf must be int$'):
            ProcInt('dummy string', 0)

    def test_bad_type_sup(self):
        with pytest.raises(TypeError, match='^ProcInt\(\) argument sup must be int$'):
            ProcInt(0, None)

    def test_bad_reversed_args(self):
        with pytest.raises(ValueError, match='^Invalid interval bounds$'):
            ProcInt(42, 1)


# pylint: disable=no-self-use,too-many-public-methods
class TestImmutability:
    def test_assign_inf(self):
        with pytest.raises(AttributeError):
            itv = ProcInt(1, 2)
            itv.inf = 0

    def test_assign_sup(self):
        with pytest.raises(AttributeError):
            itv = ProcInt(1, 2)
            itv.sup = 5


# pylint: disable=no-self-use,too-many-public-methods
class TestDisplay:
    def test_point(self):
        itv = ProcInt(0, 0)
        assert str(itv) == '0'
        assert format(itv, ':') == '0'
        assert format(itv) == str(itv)
        assert repr(itv) == 'ProcInt(inf=0, sup=0)'
        assert itv == eval(repr(itv))

    def test_wide(self):
        itv = ProcInt(0, 41)
        assert str(itv) == '0-41'
        assert format(itv, ':') == '0:41'
        assert format(itv) == str(itv)
        assert repr(itv) == 'ProcInt(inf=0, sup=41)'
        assert itv == eval(repr(itv))

    def test_bad_format_spec(self):
        with pytest.raises(ValueError, match='^Invalid format specifier$'):
            format(ProcInt(0, 2), '--')


# pylint: disable=no-self-use
class TestCopy:
    def test_copy(self):
        itv = ProcInt(0, 0)
        copy_itv = copy.copy(itv)
        assert copy_itv == itv
        assert copy_itv is not itv

    def test_deepcopy(self):
        itv = ProcInt(0, 0)
        copy_itv = copy.deepcopy(itv)
        assert copy_itv == itv
        assert copy_itv is not itv
