from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
import unittest

from amaascore.core.tenor import Tenor


class TenorTest(unittest.TestCase):

    def test_CheckTenor(self):
        tenor = Tenor('10Y')
        self.assertEqual(tenor.tenor, '10Y')
        with self.assertRaisesRegexp(ValueError, 'Invalid tenor'):
            tenor = Tenor('100M')

    def test_TenorToTimedelta(self):
        tenor = Tenor('1M')
        start_date = date(2000, 2, 1)
        end_date = start_date + tenor.to_relativedelta()
        self.assertEqual(end_date, date(2000, 3, 1))

if __name__ == '__main__':
    unittest.main()
