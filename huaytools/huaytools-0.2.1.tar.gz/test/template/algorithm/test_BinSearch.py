from __future__ import print_function

import unittest
from unittest import TestCase

from huaytools.template.algorithm.search import BinSearch


class TestBinSearch(TestCase):
    def setUp(self):
        self.bs = BinSearch()

    def test_lower_bound(self):
        xs = [1, 2, 3]
        target = 2
        ex_ret = 1
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

        xs = [1, 2, 2, 2, 3]
        target = 2
        ex_ret = 1
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

        xs = [1, 2, 3]
        target = 0
        ex_ret = 0
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

        xs = [1, 2, 3]
        target = 5
        ex_ret = 3
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

    def test_upper_bound(self):
        xs = [1, 2, 3]
        target = 2
        ex_ret = 2
        self.assertEqual(self.bs.upper_bound(xs, target), ex_ret)

        xs = [1, 2, 2, 2, 3]
        target = 2
        ex_ret = 4
        self.assertEqual(self.bs.upper_bound(xs, target), ex_ret)

        xs = [1, 2, 3]
        target = 0
        ex_ret = 0
        self.assertEqual(self.bs.upper_bound(xs, target), ex_ret)

        xs = [1, 2, 3]
        target = 5
        ex_ret = 3
        self.assertEqual(self.bs.upper_bound(xs, target), ex_ret)

    def test_bin_search(self):
        xs = [1, 2, 3]
        target = 2
        ex_ret = 1
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

        xs = [1, 2, 2, 2, 3]
        target = 2
        ex_ret = 1
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

        xs = [1, 2, 3]
        target = 0
        ex_ret = 0
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

        xs = [1, 2, 3]
        target = 5
        ex_ret = 3
        self.assertEqual(self.bs.lower_bound(xs, target), ex_ret)

    def test_bin_search_float(self):
        lb, ub = 3, 4
        ex_ret = 3.141
        self.assertEqual(self.bs.bin_search_float(lb, ub), ex_ret)

        lb, ub = 3, 4
        ex_ret = 3.1401
        self.assertEqual(self.bs.bin_search_float(lb, ub, precision=0.0001), ex_ret)

        lb, ub = -1, 10000
        ex_ret = 3.1401
        self.assertEqual(self.bs.bin_search_float(lb, ub, precision=0.0001), ex_ret)

    def test_bin_search_float_while(self):
        lb, ub = 3, 4
        ex_ret = 3.141
        self.assertEqual(self.bs.bin_search_float_while(lb, ub), ex_ret)

        lb, ub = 3, 4
        ex_ret = 3.1401
        self.assertEqual(self.bs.bin_search_float_while(lb, ub, precision=0.0001), ex_ret)

        lb, ub = -1, 10000
        ex_ret = 3.1401
        self.assertEqual(self.bs.bin_search_float_while(lb, ub, precision=0.0001), ex_ret)


if __name__ == '__main__':
    unittest.main()
