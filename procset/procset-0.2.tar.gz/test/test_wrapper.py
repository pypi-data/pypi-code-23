# -*- coding: utf-8 -*-

# Copyright © 2017
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

import pytest
import interval_set.interval_set as oldapi
import intsetwrap as newapi


# pylint: disable=no-self-use,too-many-public-methods
class TestCompatibility:
    def test_itvs2str(self):
        new = newapi.interval_set_to_string([(1, 2), (5, 5), (10, 50)])
        old = oldapi.interval_set_to_string([(1, 2), (5, 5), (10, 50)])
        assert new == old

    @pytest.mark.xfail(reason="bug in reference implementation")
    def test_str2itvs_1(self):
        new = newapi.string_to_interval_set("1 2 3 7-9 13")
        old = oldapi.string_to_interval_set("1 2 3 7-9 13")
        assert new == old

    def test_str2itvs_2(self):
        new = newapi.string_to_interval_set("")
        old = oldapi.string_to_interval_set("")
        assert new == old

    def test_str2itvs_3(self):
        with pytest.raises(ValueError):
            newapi.string_to_interval_set("(2,3)")
        with pytest.raises(ValueError):
            oldapi.string_to_interval_set("(2,3)")

    def test_itvs2list_1(self):
        new = newapi.interval_set_to_id_list([])
        old = oldapi.interval_set_to_id_list([])
        assert new == old

    def test_itvs2list_2(self):
        new = newapi.interval_set_to_id_list([(1, 1), (3, 4)])
        old = oldapi.interval_set_to_id_list([(1, 1), (3, 4)])
        assert new == old

    def test_list2itvs_1(self):
        new = newapi.id_list_to_iterval_set([])
        old = oldapi.id_list_to_iterval_set([])
        assert new == old

    def test_list2itvs_2(self):
        new = newapi.id_list_to_iterval_set([1, 2, 5, 7, 9, 10, 11])
        old = oldapi.id_list_to_iterval_set([1, 2, 5, 7, 9, 10, 11])
        assert new == old

    def test_itvs2set_1(self):
        new = newapi.interval_set_to_set([])
        old = oldapi.interval_set_to_set([])
        assert new == old

    def test_itvs2set_2(self):
        new = newapi.interval_set_to_set([(1, 1), (3, 4)])
        old = oldapi.interval_set_to_set([(1, 1), (3, 4)])
        assert new == old

    def test_set2itvs_1(self):
        new = newapi.set_to_interval_set(set())
        old = oldapi.set_to_interval_set(set())
        assert new == old

    def test_set2itvs_2(self):
        new = newapi.set_to_interval_set({1, 2, 5, 7, 9, 10, 11})
        old = oldapi.set_to_interval_set({1, 2, 5, 7, 9, 10, 11})
        assert new == old

    def test_total_1(self):
        new = newapi.total([])
        old = oldapi.total([])
        assert new == old

    def test_total_2(self):
        new = newapi.total([(0, 0)])
        old = oldapi.total([(0, 0)])
        assert new == old

    def test_total_3(self):
        new = newapi.total([(1, 1), (3, 4)])
        old = oldapi.total([(1, 1), (3, 4)])
        assert new == old

    def test_equals_1(self):
        new = newapi.equals([], [])
        old = oldapi.equals([], [])
        assert new == old

    def test_equals_2(self):
        new = newapi.equals([(1, 1)], [(1, 2)])
        old = oldapi.equals([(1, 1)], [(1, 2)])
        assert new == old

    def test_equals_3(self):
        new = newapi.equals([(1, 10)], [])
        old = oldapi.equals([(1, 10)], [])
        assert new == old

    def test_equals_4(self):
        new = newapi.equals([(1, 2), (3, 4)], [(1, 4)])
        old = oldapi.equals([(1, 2), (3, 4)], [(1, 4)])
        assert new == old

    def test_equals_5(self):
        new = newapi.equals([(5, 100), (3, 4)], [(3, 4), (5, 100)])
        old = oldapi.equals([(5, 100), (3, 4)], [(3, 4), (5, 100)])
        assert new == old

    def test_difference_1(self):
        new = newapi.difference([], [(1, 1)])
        old = oldapi.difference([], [(1, 1)])
        assert new == old

    def test_difference_2(self):
        new = newapi.difference([(1, 1), (3, 4)], [(1, 2), (4, 7)])
        old = oldapi.difference([(1, 1), (3, 4)], [(1, 2), (4, 7)])
        assert new == old

    def test_difference_3(self):
        new = newapi.difference([(1, 12)], [(1, 2), (4, 7)])
        old = oldapi.difference([(1, 12)], [(1, 2), (4, 7)])
        assert new == old

    def test_intersection_1(self):
        new = newapi.intersection([(1, 2), (4, 5)], [(1, 3), (5, 7)])
        old = oldapi.intersection([(1, 2), (4, 5)], [(1, 3), (5, 7)])
        assert new == old

    def test_intersection_2(self):
        new = newapi.intersection([(2, 3), (5, 7)], [(1, 1), (4, 4)])
        old = oldapi.intersection([(2, 3), (5, 7)], [(1, 1), (4, 4)])
        assert new == old

    def test_intersection_3(self):
        new = newapi.intersection([(3, 7)], [(2, 8)])
        old = oldapi.intersection([(3, 7)], [(2, 8)])
        assert new == old

    def test_intersection_4(self):
        new = newapi.intersection([(3, 7)], [(2, 6)])
        old = oldapi.intersection([(3, 7)], [(2, 6)])
        assert new == old

    def test_union(self):
        new = newapi.union([(1, 1), (3, 4)], [(1, 2), (4, 7)])
        old = oldapi.union([(1, 1), (3, 4)], [(1, 2), (4, 7)])
        assert new == old

    def test_aggregate_1(self):
        new = newapi.aggregate([])
        old = oldapi.aggregate([])
        assert new == old

    def test_aggregate_2(self):
        new = newapi.aggregate([(1, 2), (3, 4)])
        old = oldapi.aggregate([(1, 2), (3, 4)])
        assert new == old

    def test_aggregate_3(self):
        new = newapi.aggregate([(3, 4), (1, 2)])
        old = oldapi.aggregate([(3, 4), (1, 2)])
        assert new == old


def test_deprecation_warnings():
    pytest.deprecated_call(newapi.interval_set_to_id_list, [])
    pytest.deprecated_call(newapi.interval_set_to_set, [])
    pytest.deprecated_call(newapi.set_to_interval_set, set())
    pytest.deprecated_call(newapi.id_list_to_iterval_set, list())
    pytest.deprecated_call(newapi.string_to_interval_set, '')
    pytest.deprecated_call(newapi.interval_set_to_string, [])
    pytest.deprecated_call(newapi.total, [])
    pytest.deprecated_call(newapi.equals, [], [])
    pytest.deprecated_call(newapi.difference, [], [])
    pytest.deprecated_call(newapi.intersection, [], [])
    pytest.deprecated_call(newapi.union, [], [])
    pytest.deprecated_call(newapi.aggregate, [])
