# -*- coding: utf-8 -*-

import unittest

from pipesnake.transformers.dropper import DropDuplicates
from pipesnake.transformers.dropper import DropNanRows


class TestDropper(unittest.TestCase):
    def test_drop_duplicates(self):
        from _data import x
        from _data import y

        dropper = DropDuplicates()
        x_new, y_new = dropper.fit_transform(x, y)
        self.assertEqual(x_new.shape[1], 1, 'x mismatch sizes: {} != 1'.format(x_new.shape[1]))
        self.assertEqual(y_new.shape[1], 2, 'y mismatch sizes: {} != 1'.format(y_new.shape[1]))

        del x, y, x_new, y_new

    def test_drop_nan_rows(self):
        from _data import x_nan
        from _data import y_nan

        dropper = DropNanRows()
        x_new, y_new = dropper.fit_transform(x_nan, y_nan)
        self.assertEqual(x_new.shape[0], 4, 'x mismatch sizes: {} != 1'.format(x_new.shape[0]))
        self.assertEqual(y_new.shape[0], 4, 'y mismatch sizes: {} != 1'.format(x_new.shape[0]))

        del x_nan, y_nan, x_new, y_new
