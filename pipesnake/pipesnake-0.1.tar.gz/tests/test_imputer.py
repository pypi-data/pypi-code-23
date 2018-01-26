# -*- coding: utf-8 -*-

import unittest

import pandas

from pipesnake.pipe import SeriesPipe
from pipesnake.transformers.imputer import KnnImputer
from pipesnake.transformers.imputer import ReplaceImputer
from pipesnake.transformers.selector import ColumnSelector


class TestImputer(unittest.TestCase):
    def test_replace_imputer(self):
        from _data import x_nan
        from _data import y_nan

        pipe = SeriesPipe(transformers=[
            ColumnSelector(x_cols=['x_1', 'x_2', 'x_3', 'x_4'], y_cols=['y_1', 'y_2']),
            ReplaceImputer(x_cols='all', y_cols='all'),
        ])
        x_new, y_new = pipe.fit_transform(x_nan, y_nan)
        self.assertEqual(pandas.isnull(x_new).any().any(), False, 'NaN values has been found in x_new')
        self.assertEqual(pandas.isnull(y_new).any().any(), False, 'NaN values has been found in y_new')

        del x_nan, y_nan, x_new, y_new

    def test_knn_imputer(self):
        from _data import x_nan
        from _data import y_nan

        imputer = KnnImputer(x_cols='all', y_cols='all')
        x_new, y_new = imputer.fit_transform(x_nan, y_nan)
        self.assertEqual(pandas.isnull(x_new).any().any(), False, 'NaN values has been found in x_new')
        self.assertEqual(pandas.isnull(y_new).any().any(), False, 'NaN values has been found in y_new')

        del x_nan, y_nan, x_new, y_new
