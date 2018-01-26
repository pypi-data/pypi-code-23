# -*- coding: utf-8 -*-

import unittest

from pipesnake.transformers.misc import ColumnRenamer


class TestBase(unittest.TestCase):
    def test_renamer(self):
        from _data import x
        from _data import y

        renamer = ColumnRenamer(prefix='test_')
        x_new, y_new = renamer.fit_transform(x, y)

        for c in x_new.columns.values:
            self.assertEqual(c.startswith('test_x_'), True, 'wrong column name: {}'.format(c))

        for c in y_new.columns.values:
            self.assertEqual(c.startswith('test_y_'), True, 'wrong column name: {}'.format(c))

        x_org, y_org = renamer.inverse_transform(x_new, y_new)

        for c in x_org.columns.values:
            self.assertEqual(c.startswith('x_'), True, 'wrong column name: {}'.format(c))

        for c in y_org.columns.values:
            self.assertEqual(c.startswith('y_'), True, 'wrong column name: {}'.format(c))

        del x, y, x_new, y_new, x_org, y_org
