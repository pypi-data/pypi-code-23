# -*- coding: utf-8 -*-

import unittest

from numpy import int64

from pipesnake.transformers.converter import Category2Number


class TestConverter(unittest.TestCase):
    def test_category_to_number(self):
        from _data import x_str
        from _data import y_str

        cat2num = Category2Number(x_cols=['x_5'], y_cols=['y_3'])
        x_new, y_new = cat2num.fit_transform(x_str, y_str)

        for item in x_new['x_5'].values:
            self.assertEqual(type(item) == int64, True, 'error: {} should be an int got: {}'.format(item, type(item)))

        for item in y_new['y_3'].values:
            self.assertEqual(type(item) == int64, True, 'error: {} should be an int got: {}'.format(item, type(item)))

        x_org, y_org = cat2num.inverse_transform(x_new, y_new)

        for a, b in zip(x_str['x_5'].values, x_org['x_5'].values):
            self.assertEqual(a, b, 'mismatch value {} != {}'.format(a, b))

        for a, b in zip(y_str['y_3'].values, y_org['y_3'].values):
            self.assertEqual(a, b, 'mismatch value {} != {}'.format(a, b))

        del x_str, y_str, x_new, y_new
