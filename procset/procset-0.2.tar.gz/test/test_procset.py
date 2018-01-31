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
from procset import ProcInt, ProcSet


# pylint: disable=no-self-use,too-many-public-methods
class TestNew:
    def test_empty(self):
        pset = ProcSet()
        assert list(pset) == []
        assert len(pset) == 0
        assert pset.count() == 0

    def test_empty_iter(self):
        pset = ProcSet(*[])
        assert list(pset) == []
        assert len(pset) == 0
        assert pset.count() == 0

    def test_single_procint(self):
        pset = ProcSet(ProcInt(0, 3))
        assert list(pset) == [0, 1, 2, 3]
        assert len(pset) == 4
        assert pset.count() == 1

    def test_single_tuple(self):
        pset = ProcSet((0, 3))
        assert list(pset) == [0, 1, 2, 3]
        assert len(pset) == 4
        assert pset.count() == 1

    def test_many_procint(self):
        pset = ProcSet(ProcInt(0, 3), ProcInt(2, 3))
        assert list(pset) == [0, 1, 2, 3]
        assert len(pset) == 4
        assert pset.count() == 1

    def test_disjoint_tuple_iter(self):
        itvs = [(0, 1), (4, 7)]
        pset = ProcSet(*itvs)
        assert list(pset) == [0, 1, 4, 5, 6, 7]
        assert len(pset) == 6
        assert pset.count() == 2

    def test_mixed_itvs(self):
        pset = ProcSet(ProcInt(0, 3), (2, 3), [4, 7])
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]
        assert len(pset) == 8
        assert pset.count() == 1

    def test_bad_iter(self):
        with pytest.raises(ValueError):
            ProcSet([])

    def test_single_int(self):
        pset = ProcSet(0)
        assert list(pset) == [0]
        assert len(pset) == 1
        assert pset.count() == 1

    def test_many_ints(self):
        pset = ProcSet(0, 1, 2)
        assert list(pset) == [0, 1, 2]
        assert len(pset) == 3
        assert pset.count() == 1

    def test_mixed_procint_int(self):
        pset = ProcSet(0, (2, 3))
        assert list(pset) == [0, 2, 3]
        assert len(pset) == 3
        assert pset.count() == 2

    def test_incompatible_string(self):
        # string are iterable but incompatible
        with pytest.raises(ValueError):
            ProcSet('1')  # caught because length < 1
        with pytest.raises(TypeError):
            ProcSet('12')  # caught because not an int
        with pytest.raises(ValueError):
            ProcSet('1-2')  # caught because length is > 2

    def test_bad_noiter(self):
        with pytest.raises(TypeError):
            ProcSet(None)


# pylint: disable=no-self-use,too-many-public-methods
class TestMisc:
    def test_equal(self):
        pset1 = ProcSet(ProcInt(0, 0))
        pset2 = ProcSet(ProcInt(0, 0))
        assert id(pset1) != id(pset2)
        assert pset1 == pset2

    def test_noequal(self):
        pset1 = ProcSet(ProcInt(0, 0))
        pset2 = ProcSet(ProcInt(0, 1))
        assert id(pset1) != id(pset2)
        assert pset1 != pset2

    def test_aggregate_empty(self):
        pset = ProcSet()
        hull = ProcSet()
        assert pset.aggregate() == hull

    def test_aggregate_point(self):
        pset = ProcSet(0)
        hull = ProcSet(0)
        assert pset.aggregate() == hull

    def test_aggregate_single_interval(self):
        pset = ProcSet((0, 7))
        hull = ProcSet((0, 7))
        assert pset.aggregate() == hull

    def test_aggregate_many_interval(self):
        pset = ProcSet((0, 1), (3, 4), (6, 7))
        hull = ProcSet((0, 7))
        assert pset.aggregate() == hull

    def test_iter_empty(self):
        pset = ProcSet()
        assert list(pset) == []
        assert list(reversed(pset)) == list(reversed(list(pset)))

    def test_iter_point(self):
        pset = ProcSet(0)
        assert list(pset) == [0]
        assert list(reversed(pset)) == list(reversed(list(pset)))

    def test_iter_single_interval(self):
        pset = ProcSet((0, 1))
        assert list(pset) == [0, 1]
        assert list(reversed(pset)) == list(reversed(list(pset)))

    def test_iter_many_interval(self):
        pset = ProcSet((0, 1), (4, 7))
        assert list(pset) == [0, 1, 4, 5, 6, 7]
        assert list(reversed(pset)) == list(reversed(list(pset)))

    def test_in_empty(self):
        assert 0 not in ProcSet()

    def test_in_single_point(self):
        assert 0 in ProcSet(0)
        assert 1 not in ProcSet(0)

    def test_in_single_interval(self):
        pset = ProcSet((0, 7))
        for proc in range(0, 8):
            assert proc in pset
        assert 8 not in pset

    def test_in_many_points(self):
        pset = ProcSet(*range(0, 8, 2))
        for proc in range(0, 8, 2):
            assert proc in pset
        for proc in range(1, 10, 2):
            assert proc not in pset

    def test_in_many_intervals(self):
        pset = ProcSet((0, 3), (8, 11), (16, 19))
        for proc in [*range(0, 4), *range(8, 12), *range(16, 20)]:
            assert proc in pset
        for proc in [*range(4, 8), *range(12, 16), *range(20, 24)]:
            assert proc not in pset

    def test_in_mixed_points_intervals(self):
        pset = ProcSet((0, 3), 8, 10, (16, 19))
        for proc in [*range(0, 4), 8, 10, *range(16, 20)]:
            assert proc in pset
        for proc in [*range(4, 8), 9, 11, *range(12, 16), *range(20, 24)]:
            assert proc not in pset

    def test_min_max_empty(self):
        with pytest.raises(ValueError, match='^empty ProcSet$'):
            ProcSet().min
        with pytest.raises(ValueError, match='^empty ProcSet$'):
            ProcSet().max

    def test_min_max_single_point(self):
        pset = ProcSet(0)
        assert pset.min == pset.max == 0

    def test_min_max_single_interval(self):
        pset = ProcSet((0, 7))
        assert pset.min == 0
        assert pset.max == 7

    def test_min_max_many_points(self):
        pset = ProcSet(0, 3, 4, 7)
        assert pset.min == 0
        assert pset.max == 7

    def test_min_max_many_intervals(self):
        pset = ProcSet((12, 25), (0, 7))
        assert pset.min == 0
        assert pset.max == 25

    def test_intervals_empty(self):
        assert list(ProcSet().intervals()) == []

    def test_intervals_single_point(self):
        assert list(ProcSet(0).intervals()) == [(0, 0)]

    def test_intervals_single_interval(self):
        assert list(ProcSet((0, 1)).intervals()) == [(0, 1)]

    def test_intervals_many_points(self):
        assert list(ProcSet(0, 2, 4).intervals()) == [(0, 0), (2, 2), (4, 4)]

    def test_intervals_many_intervals(self):
        assert list(ProcSet((6, 7), (0, 3)).intervals()) == [(0, 3), (6, 7)]

    def test_intervals_mixed_points_intervals(self):
        assert list(ProcSet((6, 7), 12, (0, 3)).intervals()) == [(0, 3), (6, 7), (12, 12)]

    def test_iscontiguous_empty(self):
        assert ProcSet().iscontiguous()

    def test_iscontiguous_single_point(self):
        assert ProcSet(1).iscontiguous()

    def test_iscontiguous_single_interval(self):
        assert ProcSet((0, 2)).iscontiguous()

    def test_iscontiguous_many_points(self):
        assert not ProcSet(0, 4).iscontiguous()

    def test_iscontiguous_many_intervals(self):
        assert not ProcSet((0, 2), (4, 7)).iscontiguous()

    def test_iscontiguous_mixed_points_intervals(self):
        assert not ProcSet(0, (3, 5)).iscontiguous()


# pylint: disable=no-self-use,too-many-public-methods
class TestStringParsing:
    def test_empty(self):
        pset = ProcSet.from_str('')
        assert pset == ProcSet()

    def test_single_point(self):
        pset = ProcSet.from_str('0')
        assert pset == ProcSet(0)

    def test_contiguous(self):
        pset = ProcSet.from_str('0-3')
        assert pset == ProcSet(ProcInt(0, 3))

    def test_disjoint_pp(self):
        pset = ProcSet.from_str('1 2')
        assert pset == ProcSet(1, 2)

    def test_disjoint_ip(self):
        pset = ProcSet.from_str('0-1 2')
        assert pset == ProcSet(ProcInt(0, 1), 2)

    def test_disjoint_ii(self):
        pset = ProcSet.from_str('0-1 2-3')
        assert pset == ProcSet(ProcInt(0, 3))

    def test_nostring(self):
        with pytest.raises(TypeError, match='^from_str\(\) argument 2 must be str, not int$'):
            ProcSet.from_str(42)

    def test_missing_left(self):
        with pytest.raises(ValueError, match='^Invalid interval format, parsed string is: -1$'):
            ProcSet.from_str('-1')

    def test_missing_right(self):
        with pytest.raises(ValueError, match='^Invalid interval format, parsed string is: 0-$'):
            ProcSet.from_str('0-')

    def test_many_contig(self):
        with pytest.raises(ValueError, match='^Invalid interval format, parsed string is: 1-2-3$'):
            ProcSet.from_str('1-2-3')


# pylint: disable=no-self-use,too-many-public-methods
class TestDisplay:
    def test_empty(self):
        pset = ProcSet()
        assert str(pset) == ''
        assert format(pset, ':,') == ''
        assert format(pset) == str(pset)
        assert format(pset, '') == str(pset)
        assert repr(pset) == 'ProcSet()'
        assert pset == eval(repr(pset))

    def test_single_point(self):
        pset = ProcSet(ProcInt(0, 0))
        assert str(pset) == '0'
        assert format(pset, ':,') == '0'
        assert format(pset) == str(pset)
        assert format(pset, '') == str(pset)
        assert repr(pset) == 'ProcSet(0)'
        assert pset == eval(repr(pset))

    def test_small(self):
        pset = ProcSet(ProcInt(0, 1))
        assert str(pset) == '0-1'
        assert format(pset, ':,') == '0:1'
        assert format(pset) == str(pset)
        assert format(pset, '') == str(pset)
        assert repr(pset) == 'ProcSet((0, 1))'
        assert pset == eval(repr(pset))

    def test_contiguous(self):
        pset = ProcSet(ProcInt(0, 7))
        assert str(pset) == '0-7'
        assert format(pset, ':,') == '0:7'
        assert format(pset) == str(pset)
        assert format(pset, '') == str(pset)
        assert repr(pset) == 'ProcSet((0, 7))'
        assert pset == eval(repr(pset))

    def test_disjoint(self):
        pset = ProcSet(ProcInt(0, 3), ProcInt(7, 15))
        assert str(pset) == '0-3 7-15'
        assert format(pset, ':,') == '0:3,7:15'
        assert format(pset) == str(pset)
        assert format(pset, '') == str(pset)
        assert repr(pset) == 'ProcSet((0, 3), (7, 15))'
        assert pset == eval(repr(pset))

    def test_bad_format_spec_short(self):
        with pytest.raises(ValueError, match='^Invalid format specifier$'):
            format(ProcSet(), ';')

    def test_bad_format_spec_long(self):
        with pytest.raises(ValueError, match='^Invalid format specifier$'):
            format(ProcSet(), ':--')


# pylint: disable=no-self-use,too-many-public-methods
class TestAdd:
    def test_empty(self):
        """
        init:  -∞................+∞
        add:   -∞....[______]....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet()
        pset.add(ProcInt(0, 7))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_strict_subset(self):
        """
        init:  -∞....[______]....+∞
        add:   -∞......[]........+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 7))
        pset.add(ProcInt(2, 3))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_strict_superset(self):
        """
        init:  -∞......[]........+∞
        add:   -∞....[______]....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(2, 3))
        pset.add(ProcInt(0, 7))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_left_disjoint_notouch(self):
        """
        init:  -∞........[__]....+∞
        add:   -∞....[]..........+∞
        final: -∞....[]..[__]....+∞
        """
        pset = ProcSet(ProcInt(4, 7))
        pset.add(ProcInt(0, 1))
        assert len(pset) == 6
        assert pset.count() == 2
        assert list(pset) == [0, 1, 4, 5, 6, 7]

    def test_right_disjoint_notouch(self):
        """
        init:  -∞....[__]........+∞
        add:   -∞..........[]....+∞
        final: -∞....[__]..[]....+∞
        """
        pset = ProcSet(ProcInt(0, 3))
        pset.add(ProcInt(6, 7))
        assert len(pset) == 6
        assert pset.count() == 2
        assert list(pset) == [0, 1, 2, 3, 6, 7]

    def test_left_disjoint_touch(self):
        """
        init:  -∞........[__]....+∞
        add:   -∞......[]........+∞
        final: -∞......[____]....+∞
        """
        pset = ProcSet(ProcInt(4, 7))
        pset.add(ProcInt(2, 3))
        assert len(pset) == 6
        assert pset.count() == 1
        assert list(pset) == [2, 3, 4, 5, 6, 7]

    def test_right_disjoint_touch(self):
        """
        init:  -∞....[__]........+∞
        add:   -∞........[]......+∞
        final: -∞....[____]......+∞
        """
        pset = ProcSet(ProcInt(0, 3))
        pset.add(ProcInt(4, 5))
        assert len(pset) == 6
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5]

    def test_left_intersect(self):
        """
        init:  -∞......[____]....+∞
        add:   -∞....[____]......+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(2, 7))
        pset.add(ProcInt(0, 5))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_right_intersect(self):
        """
        init:  -∞....[____]......+∞
        add:   -∞......[____]....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 5))
        pset.add(ProcInt(2, 7))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_between_disjoint_notouch(self):
        """
        init:  -∞....[]....[]....+∞
        add:   -∞.......[].......+∞
        final: -∞....[].[].[]....+∞
        """
        pset = ProcSet(ProcInt(0, 1), ProcInt(6, 7))
        pset.add(ProcInt(3, 4))
        assert len(pset) == 6
        assert pset.count() == 3
        assert list(pset) == [0, 1, 3, 4, 6, 7]

    def test_between_disjoint_touch(self):
        """
        init:  -∞....[]....[]....+∞
        add:   -∞......[__]......+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 1), ProcInt(6, 7))
        pset.add(ProcInt(2, 5))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_between_intersect(self):
        """
        init:  -∞....[_]..[_]....+∞
        add:   -∞.....[___]......+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 2), ProcInt(5, 7))
        pset.add(ProcInt(1, 5))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_superset_left_notouch(self):
        """
        init:  -∞.....[]..[_]....+∞
        add:   -∞....[_____].....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(1, 2), ProcInt(5, 7))
        pset.add(ProcInt(0, 6))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_superset_left_touch(self):
        """
        init:  -∞....[_]..[_]....+∞
        add:   -∞....[_____].....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 2), ProcInt(5, 7))
        pset.add(ProcInt(0, 6))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_superset_right_notouch(self):
        """
        init:  -∞....[_]..[].....+∞
        add:   -∞.....[_____]....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 2), ProcInt(5, 6))
        pset.add(ProcInt(1, 7))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_superset_right_touch(self):
        """
        init:  -∞....[_]..[_]....+∞
        add:   -∞.....[_____]....+∞
        final: -∞....[______]....+∞
        """
        pset = ProcSet(ProcInt(0, 2), ProcInt(5, 7))
        pset.add(ProcInt(1, 7))
        assert len(pset) == 8
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_englobing_superset(self):
        """
        init:  -∞.....[].[]......+∞
        add:   -∞....[_____].....+∞
        final: -∞....[_____].....+∞
        """
        pset = ProcSet(ProcInt(1, 2), ProcInt(4, 5))
        pset.add(ProcInt(0, 6))
        assert len(pset) == 7
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4, 5, 6]

    def test_left_disjoint_point_notouch(self):
        """
        init:  -∞........[__]....+∞
        add:   -∞....X...........+∞
        final: -∞....X...[__]....+∞
        """
        pset = ProcSet(ProcInt(4, 7))
        pset.add(ProcInt(0, 0))
        assert len(pset) == 5
        assert pset.count() == 2
        assert list(pset) == [0, 4, 5, 6, 7]

    def test_right_disjoint_point_notouch(self):
        """
        init:  -∞....[__]........+∞
        add:   -∞...........X....+∞
        final: -∞....[__]...X....+∞
        """
        pset = ProcSet(ProcInt(0, 3))
        pset.add(ProcInt(7, 7))
        assert len(pset) == 5
        assert pset.count() == 2
        assert list(pset) == [0, 1, 2, 3, 7]

    def test_left_disjoint_point_touch(self):
        """
        init:  -∞........[__]....+∞
        add:   -∞.......X........+∞
        final: -∞.......[___]....+∞
        """
        pset = ProcSet(ProcInt(4, 7))
        pset.add(ProcInt(3, 3))
        assert len(pset) == 5
        assert pset.count() == 1
        assert list(pset) == [3, 4, 5, 6, 7]

    def test_right_disjoint_point_touch(self):
        """
        init:  -∞....[__]........+∞
        add:   -∞........X.......+∞
        final: -∞....[___].......+∞
        """
        pset = ProcSet(ProcInt(0, 3))
        pset.add(ProcInt(4, 4))
        assert len(pset) == 5
        assert pset.count() == 1
        assert list(pset) == [0, 1, 2, 3, 4]

    def test_single_point(self):
        pset = ProcSet()
        pset.add(0)
        assert len(pset) == 1
        assert pset.count() == 1
        assert list(pset) == [0]

    def test_incompatible_iter(self):
        with pytest.raises(ValueError):
            pset = ProcSet()
            pset.add((0, 1, 2))  # too many
        with pytest.raises(ValueError):
            pset = ProcSet()
            pset.add((0, ))  # too few


# pylint: disable=no-self-use,protected-access,too-many-public-methods
class TestCopy:
    def test_copy_empty(self):
        pset = ProcSet()
        copy_pset = copy.copy(pset)
        assert copy_pset == pset
        assert copy_pset is not pset
        assert copy_pset._itvs is not pset._itvs

    def test_copy_nonempty(self):
        pset = ProcSet(ProcInt(0, 3))
        copy_pset = copy.copy(pset)
        assert copy_pset == pset
        assert copy_pset is not pset
        assert copy_pset._itvs is not pset._itvs

    def test_deepcopy_empty(self):
        pset = ProcSet()
        copy_pset = copy.deepcopy(pset)
        assert copy_pset == pset
        assert copy_pset is not pset
        assert copy_pset._itvs is not pset._itvs

    def test_deepcopy_nonempty(self):
        pset = ProcSet(ProcInt(0, 3))
        copy_pset = copy.deepcopy(pset)
        assert copy_pset == pset
        assert copy_pset is not pset
        assert copy_pset._itvs is not pset._itvs
