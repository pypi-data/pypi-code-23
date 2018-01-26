# -*- coding: utf-8 -*-

import unittest

from pipesnake.pipe import ParallelPipe
from pipesnake.pipe import SeriesPipe
from pipesnake.transformers.selector import ColumnSelector


class TestPipe(unittest.TestCase):
    def test_aseries(self):
        from _data import x
        from _data import y

        transformers = [ColumnSelector(x_cols=['x_3', 'x_4', ]),
                        ColumnSelector(x_cols=['x_4', ], y_cols=['y_1', ]), ]
        pipe = SeriesPipe(transformers=transformers)
        x_new, y_new = pipe.fit_transform(x, y)
        self.assertEqual(len(pipe), len(transformers),
                         'Mismatched size {} != {}'.format(len(pipe), len(transformers)))
        self.assertEqual(len(x_new.columns), 1, 'Mismatched size {} != 1'.format(len(x_new.columns)))
        self.assertEqual(len(y_new.columns), 1, 'Mismatched size {} != 1'.format(len(y_new.columns)))

        del x, y, x_new, y_new

    def test_parallel(self):
        from _data import x
        from _data import y

        transformers = [ColumnSelector(x_cols=['x_1', 'x_2', 'x_3', 'x_4', ], y_cols=['y_1', ], name='1'),
                        ColumnSelector(x_cols=['x_3', ], name='2'), ]
        pipe = ParallelPipe(transformers=transformers)
        x_new, y_new = pipe.fit_transform(x, y)
        self.assertEqual(len(pipe), len(transformers),
                         'Mismatched size {} != {}'.format(len(pipe), len(transformers)))
        self.assertEqual(len(x_new.columns), 5, 'Mismatched size {} != 5'.format(len(x_new.columns)))
        self.assertEqual(len(y_new.columns), 3, 'Mismatched size {} != 3'.format(len(y_new.columns)))

        del x, y, x_new, y_new

    def test_both(self):
        from _data import x
        from _data import y

        pipe = SeriesPipe(transformers=[
            ParallelPipe(transformers=[
                ColumnSelector(x_cols=['x_1', 'x_2', 'x_3', 'x_4', ], y_cols=['y_1', ], name='1'),
                ColumnSelector(x_cols=['x_3', ], name='2'),
            ]),
            ColumnSelector(x_cols=['x_1_1', ], y_cols=['y_1_1', ], name='3'),
        ])
        x_new, y_new = pipe.fit_transform(x, y)
        self.assertEqual(len(x_new.columns), 1, 'Mismatched size {} != 1'.format(len(x_new.columns)))
        self.assertEqual(len(y_new.columns), 1, 'Mismatched size {} != 1'.format(len(y_new.columns)))

        del x, y, x_new, y_new
