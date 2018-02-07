import sys
import os
import unittest

import pandas as pd
import numpy as np

from vaquero.util import *

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


class TestUtil(unittest.TestCase):

    def test_first(self):
        def f():
            yield 10
            yield 20

        self.assertEqual(first(f()), 10)

    def test_nth(self):
        def f():
            yield 10
            yield 20
            yield 30

        self.assertEqual(nth(f(), 1), 20)

    def test_take(self):
        self.assertEqual(list(take(range(1000), 2)), [0, 1])

    def test_tap(self):
        accumulator = []

        def gobble(x):
            accumulator.append(x)

        total = sum(x for x in tap(range(10), gobble))
        self.assertEqual(total, sum(accumulator))

    def test_find(self):
        self.assertEqual(find([1, 2, 3, 4], lambda x: x > 1), 2)
        self.assertEqual(find(reversed([1, 2, 3, 4]), lambda x: x > 1), 4)
        self.assertIsNone(find([1, 2, 3, 4], lambda x: x > 10))

    def test_jsonlines_reader(self):
        file_path = os.path.join(THIS_DIR, "demo.jsonlines")
        reader = jsonlines_reader(file_path, True)
        expected = [{"first": "Bob", "age": 32},
                    {"first": "Alice", "age": 33}]
        self.assertEqual(list(reader), expected)

        with self.assertRaises(ValueError):
            list(jsonlines_reader(file_path, False))

    def test_slurp(self):
        s = slurp(os.path.join(THIS_DIR, "fixtures", "files_processor",
                               "hello.txt"))
        self.assertEqual(s, "hello")
        pass

    def test_pd_print_entirely(self):
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        series = pd.Series(range(1000))
        pd_print_entirely(series)
        self.assertEqual(1001, len(sys.stdout.getvalue().splitlines()))

    def test_examine_pairwise_res(self):
        src = {'x': 100}

        def f(s, d):
            d['x'] = s['x'] ** 2

        res = examine_pairwise_result(f, src)
        self.assertEqual(res['x'], 10000)

    def test_np_and(self):
        x = np.arange(10)
        res = list(x[np_and(x > 5, x % 2 == 0)])
        self.assertEqual(res, [6, 8])

    def test_np_or(self):
        x = np.arange(10)
        res = list(x[np_or(x > 5, x % 2 == 0)])
        self.assertEqual(res, [0, 2, 4, 6, 7, 8, 9])

    def test_files_processor(self):
        file_path = os.path.join(THIS_DIR, "fixtures", "files_processor")
        items = files_processor(slurp, file_path, "*.txt", recursive=True)
        self.assertEqual(list(items), list("hellogoodbye"))

        items = files_processor(slurp, file_path, "*.txt", recursive=False)
        self.assertEqual(list(items), list("hello"))

    def test_op_collector(self):
        d = {}

        with self.assertRaises(KeyError):
            ops = OpCollector(d)
            del ops['x']
            ops.apply_all()

        with self.assertRaises(AttributeError):
            ops = OpCollector(d)
            ops.doesnt_exist(10)

        ops = OpCollector(d, eager=False)
        ops.doesnt_exist(10)

        d = {}
        ops = OpCollector(d, swallow_exceptions=[KeyError])
        ops['y'] = 20
        del ops['x']
        self.assertEqual(ops.apply_all(), 1)
        self.assertEqual(d, {'y': 20})

        called = []

        def f(x):
            called.append(x)
        ops = OpCollector(f)
        ops(10)
        self.assertEqual(str(ops), repr(ops))
        self.assertEqual(str(ops), "OpCollector([1 ops ready for processing])")
        self.assertEqual(ops.ops, [('__call__', (10,), {})])
        ops.apply_all()
        self.assertEqual(str(ops), "OpCollector([0 ops ready for processing])")
        self.assertEqual(called, [10])

    def test_deferred_delete(self):
        d = {'a': 20, 'b': 30, 'c': 40}
        with deferred_delete(d) as proxy:
            for k in d:
                if k == 'b':
                    del proxy[k]
        self.assertEqual({'a': 20, 'c': 40}, d)

        with deferred_delete(d) as proxy:
            del proxy['b']

        with self.assertRaises(KeyError):
            with deferred_delete(d, skip_missing=False) as proxy:
                del proxy['b']

        d = {}
        with self.assertRaises(ZeroDivisionError):
            with deferred_delete(d) as proxy:
                del proxy['a']
                proxy['a'] = 20
                1 / 0
        self.assertEqual(d, {})

    def test_chunking(self):
        expected = [[1, 2, 3], [4, 5, 6], [7, 8]]

        self.assertEqual(list(chunking(range(1, 9), 3)), expected)

    def test_not_null(self):
        items = [1, None, np.NaN, 2, 3]
        expected = [1, 2, 3]

        self.assertEqual(list(not_null(items)), expected)
