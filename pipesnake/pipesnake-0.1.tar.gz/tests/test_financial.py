# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import unittest

from pipesnake.transformers.financial import ToReturn


class TestFinancial(unittest.TestCase):
    def test_to_return(self):
        from _data import x
        from _data import y

        returner = ToReturn(x_cols='all', y_cols='all')
        x_new, y_new = returner.fit_transform(x, y)

        del x, y, x_new, y_new

