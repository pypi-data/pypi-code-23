# -*- coding: utf-8 -*-

import unittest

from pipesnake.transformers.combiner import Combiner
from pipesnake.transformers.combiner import Roller


class TestCombiner(unittest.TestCase):
    def test_combiner(self):
        from _data import x
        from _data import y

        def foo(x, y):
            return x + y + 1.0

        def inv_foo(x):
            t = (x - 1.0) / 2.0
            return t, t

        combiner = Combiner(x_cols=[['x_1', 'x_4'], ['x_2', 'x_3']],
                            y_cols=[['y_1', 'y_2']],
                            func=foo,
                            inv_func=inv_foo)
        x_new, y_new = combiner.fit_transform(x, y)
        self.assertEqual(x_new.shape[1], 2, 'mismatch sizes: {} != 2'.format(x_new.shape[1]))
        self.assertEqual(y_new.shape[1], 1, 'mismatch sizes: {} != 1'.format(y_new.shape[1]))

        for _, r in x_new.iterrows():
            self.assertEqual(r[0], r[1], 'mismatch size: {} != {}'.format(r[0], r[1]))

        for l, r, in zip(y.values.tolist(), y_new.values.tolist()):
            self.assertEqual(foo(l[0], l[1]), r[0], 'mismatch value: {} != {}'.format(l, r))

        x_org, y_org = combiner.inverse_transform(x_new, y_new)
        self.assertEqual(x_org.shape[1], 4, 'mismatch sizes: {} != 4'.format(x_org.shape[1]))
        self.assertEqual(y_org.shape[1], 2, 'mismatch sizes: {} != 2'.format(y_org.shape[1]))

        for r in y_org.values.tolist():
            self.assertEqual(r[0], r[1], 'mismatch value: {} != {}'.format(r[0], r[1]))

        del x, y, x_new, y_new, x_org, y_org

    def test_roller(self):
        from _data import x
        from _data import y

        roller = Roller(x_cols='all', y_cols='all', roll_func=lambda x: x[1], inv_roll_func=lambda x: x[1], window=2)
        x_new, y_new = roller.fit_transform(x, y)
        x_org, y_org = roller.inverse_transform(x_new, y_new)

        x_new.columns = x.columns  # in order to de able to use == below
        y_new.columns = y.columns  # in order to de able to use == below

        equals = (x == x_new).any(1)
        for i, (left, right) in enumerate(zip([False, True, True, True], equals)):
            self.assertEqual(left, right, 'mismatched values in x row {}: {} != {}'.format(i, left, right))
        equals = (y == y_new).any(1)
        for i, (left, right) in enumerate(zip([False, True, True, True], equals)):
            self.assertEqual(left, right, 'mismatched values in y row {}: {} != {}'.format(i, left, right))

        equals = (x == x_org).any(1)
        for i, (left, right) in enumerate(zip([False, False, True, True], equals)):
            self.assertEqual(left, right, 'mismatched values in x row {}: {} != {}'.format(i, left, right))
        equals = (y == y_org).any(1)
        for i, (left, right) in enumerate(zip([False, False, True, True], equals)):
            self.assertEqual(left, right, 'mismatched values in y row {}: {} != {}'.format(i, left, right))

        del x, y, x_new, y_new, x_org, y_org
