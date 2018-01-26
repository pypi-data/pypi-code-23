# -*- coding: utf-8 -*-

import unittest

from pipesnake.pipe import SeriesPipe


class TestBase(unittest.TestCase):
    def test(self):
        from _transformer import FakeTransformer

        transformers = [FakeTransformer('fake1'), FakeTransformer('fake2'), ]
        series = SeriesPipe(transformers=transformers)
        self.assertEqual(len(series), 2, 'Mismatched size {} != 2'.format(len(series)))
        series.append(FakeTransformer('fake3'))
        self.assertEqual(len(series), 3, 'Mismatched size {} != 3'.format(len(series)))

        del transformers
