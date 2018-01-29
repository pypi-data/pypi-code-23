# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals

from mo_testing.fuzzytestcase import FuzzyTestCase

from mo_collections.matrix import index_to_coordinate


class TestUniqueIndex(FuzzyTestCase):

    def test_zero_dim(self):
        f = index_to_coordinate([])

        self.assertAlmostEqual(f(-1), tuple())
        self.assertAlmostEqual(f(0), tuple())
        self.assertAlmostEqual(f(1), tuple())
        self.assertAlmostEqual(f(2), tuple())
        self.assertAlmostEqual(f(3), tuple())

    def test_one_dim(self):
        f = index_to_coordinate([2])

        # self.assertAlmostEqual(f(-1), 1,)
        self.assertAlmostEqual(f(0), (0,))
        self.assertAlmostEqual(f(1), (1,))
        # self.assertAlmostEqual(f(2), (0,))
        # self.assertAlmostEqual(f(3), (1,))

    def test_two_dim(self):
        f = index_to_coordinate([2, 3])

        # self.assertAlmostEqual(f(-1), (1, 2))
        self.assertAlmostEqual(f(0), (0,0))
        self.assertAlmostEqual(f(1), (0,1))
        self.assertAlmostEqual(f(2), (0,2))
        self.assertAlmostEqual(f(3), (1,0))
        self.assertAlmostEqual(f(4), (1,1))
        self.assertAlmostEqual(f(5), (1,2))
        # self.assertAlmostEqual(f(6), (0,0))
        # self.assertAlmostEqual(f(7), (0,1))
        # self.assertAlmostEqual(f(8), (0,2))

