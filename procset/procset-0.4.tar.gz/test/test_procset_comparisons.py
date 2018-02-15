# -*- coding: utf-8 -*-

# Copyright © 2018
# Contributed by Raphaël Bleuse <raphael.bleuse@uni.lu>
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


# The naming convention of the tests follows the one in the position paper by
# the IEEE Interval Standard Working Group - P1788.
# See docs/NehmeierM2010Interval.pdf for further informations.


import collections
from procset import ProcSet
import helpers

##### helper functions/classes #####

_TestCase = collections.namedtuple(
    '_TestCase',
    ['doc', 'left', 'right', 'expect_res']
)


def _build_comparison_test(testcase):
    def _comparison_test(self):
        left_pset = ProcSet(*testcase.left)
        right_pset = ProcSet(*testcase.right)

        # apply comparison method by name
        comparison = getattr(left_pset, self.method)(right_pset)

        # check correctness of result
        assert isinstance(comparison, bool)
        assert comparison == testcase.expect_res

    _comparison_test.__doc__ = testcase.doc

    return _comparison_test


##### testcases #####

ISDISJOINT_TESTCASES = {
    'before_ii_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞.........[_]....+∞
        result: True
        """,
        (0, 1, 2, 3, ),
        (5, 6, 7, ),
        True
    ),
    'before_ip_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞...........X....+∞
        result: True
        """,
        (0, 1, 2, 3, ),
        (7, ),
        True
    ),
    'before_pi_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....X...........+∞
        right:  -∞........[__]....+∞
        result: True
        """,
        (0, ),
        (4, 5, 6, 7, ),
        True
    ),
    'before_pp_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....X...........+∞
        right:  -∞........X.......+∞
        result: True
        """,
        (0, ),
        (4, ),
        True
    ),
    'before_ii_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞........[__]....+∞
        result: True
        """,
        (0, 1, 2, 3, ),
        (4, 5, 6, 7, ),
        True
    ),
    'before_ip_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞........X.......+∞
        result: True
        """,
        (0, 1, 2, 3, ),
        (4, ),
        True
    ),
    'before_pi_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....X...........+∞
        right:  -∞.....[_]........+∞
        result: True
        """,
        (0, ),
        (1, 2, 3, ),
        True
    ),
    'before_pp_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....X...........+∞
        right:  -∞.....X..........+∞
        result: True
        """,
        (0, ),
        (1, ),
        True
    ),
    'meets_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞.......[___]....+∞
        result: False
        """,
        (0, 1, 2, 3, ),
        (3, 4, 5, 6, 7, ),
        False
    ),
    'overlaps_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[____]......+∞
        right:  -∞......[____]....+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, ),
        (2, 3, 4, 5, 6, 7, ),
        False
    ),
    'starts_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞....[______]....+∞
        result: False
        """,
        (0, 1, 2, 3, ),
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        False
    ),
    'starts_pi': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....X...........+∞
        right:  -∞....[__]........+∞
        result: False
        """,
        (0, ),
        (0, 1, 2, 3, ),
        False
    ),
    'containedby_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞......[__]......+∞
        right:  -∞....[______]....+∞
        result: False
        """,
        (2, 3, 4, 5, ),
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        False
    ),
    'containedby_pi': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.......X........+∞
        right:  -∞....[______]....+∞
        result: False
        """,
        (3, ),
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        False
    ),
    'finishes_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞........[__]....+∞
        right:  -∞....[______]....+∞
        result: False
        """,
        (4, 5, 6, 7, ),
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        False
    ),
    'finishes_pi': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.......X........+∞
        right:  -∞....[__]........+∞
        result: False
        """,
        (3, ),
        (0, 1, 2, 3, ),
        False
    ),
    'equal_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[__]........+∞
        right:  -∞....[__]........+∞
        result: False
        """,
        (0, 1, 2, 3, ),
        (0, 1, 2, 3, ),
        False
    ),
    'equal_pp': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....X...........+∞
        right:  -∞....X...........+∞
        result: False
        """,
        (0, ),
        (0, ),
        False
    ),
    'finishedby_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[______]....+∞
        right:  -∞........[__]....+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        (4, 5, 6, 7, ),
        False
    ),
    'finishedby_ip': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[______]....+∞
        right:  -∞...........X....+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        (7, ),
        False
    ),
    'contains_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[______]....+∞
        right:  -∞......[__]......+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        (2, 3, 4, 5, ),
        False
    ),
    'contains_ip': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[______]....+∞
        right:  -∞........X.......+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        (4, ),
        False
    ),
    'startedby_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[______]....+∞
        right:  -∞....[__]........+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        (0, 1, 2, 3, ),
        False
    ),
    'startedby_ip': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[______]....+∞
        right:  -∞....X...........+∞
        result: False
        """,
        (0, 1, 2, 3, 4, 5, 6, 7, ),
        (0, ),
        False
    ),
    'overlappedby_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.......[___]....+∞
        right:  -∞....[____]......+∞
        result: False
        """,
        (3, 4, 5, 6, 7, ),
        (0, 1, 2, 3, 4, 5, ),
        False
    ),
    'metby_ii': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞....[___].......+∞
        right:  -∞........[__]....+∞
        result: False
        """,
        (0, 1, 3, 2, 4, ),
        (4, 5, 6, 7, ),
        False
    ),
    'after_ii_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞..........[]....+∞
        right:  -∞......[]........+∞
        result: True
        """,
        (6, 7, ),
        (2, 3, ),
        True
    ),
    'after_pi_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.........X......+∞
        right:  -∞....[__]........+∞
        result: True
        """,
        (5, ),
        (0, 1, 2, 3, ),
        True
    ),
    'after_ip_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞........[__]....+∞
        right:  -∞....X...........+∞
        result: True
        """,
        (4, 5, 6, 7, ),
        (0, ),
        True
    ),
    'after_pp_notouch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.......X........+∞
        right:  -∞....X...........+∞
        result: True
        """,
        (3, ),
        (0, ),
        True
    ),
    'after_ii_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞..........[]....+∞
        right:  -∞......[__]......+∞
        result: True
        """,
        (6, 7, ),
        (2, 3, 4, 5, ),
        True
    ),
    'after_pi_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.........X......+∞
        right:  -∞....[___].......+∞
        result: True
        """,
        (5, ),
        (0, 1, 2, 3, 4, ),
        True
    ),
    'after_ip_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞........[__]....+∞
        right:  -∞.......X........+∞
        result: True
        """,
        (4, 5, 6, 7, ),
        (3, ),
        True
    ),
    'after_pp_touch': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.......X........+∞
        right:  -∞......X.........+∞
        result: True
        """,
        (3, ),
        (2, ),
        True
    ),
    'firstempty_i': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞................+∞
        right:  -∞......[__]......+∞
        result: True
        """,
        (),
        (2, 3, 4, 5, ),
        True
    ),
    'firstempty_p': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞................+∞
        right:  -∞.......X........+∞
        result: True
        """,
        (),
        (3, ),
        True
    ),
    'secondempty_i': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞......[__]......+∞
        right:  -∞................+∞
        result: True
        """,
        (2, 3, 4, 5, ),
        (),
        True
    ),
    'secondempty_p': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞.......X........+∞
        right:  -∞................+∞
        result: True
        """,
        (3, ),
        (),
        True
    ),
    'bothempty': _TestCase(
        """
                -∞....01234567....+∞
        left:   -∞................+∞
        right:  -∞................+∞
        result: True
        """,
        (),
        (),
        True
    ),
}


#####  actual test classes  #####

# pylint: disable=invalid-name

TestIsDisjoint = helpers.build_test_class(
    'TestIsDisjoint',
    'isdisjoint',
    ISDISJOINT_TESTCASES,
    _build_comparison_test
)
