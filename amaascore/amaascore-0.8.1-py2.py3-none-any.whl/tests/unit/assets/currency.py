from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.currency import Currency
from amaascore.tools.generate_asset import generate_currency


class CurrencyTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.currency = generate_currency()
        self.asset_id = self.currency.asset_id

    def tearDown(self):
        pass

    def test_Currency(self):
        self.assertEqual(type(self.currency), Currency)
        self.assertEqual(self.currency.pricing_method(), 'Market')

if __name__ == '__main__':
    unittest.main()
