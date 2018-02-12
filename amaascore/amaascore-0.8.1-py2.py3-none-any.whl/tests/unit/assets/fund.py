from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.fund import Fund
from amaascore.tools.generate_asset import generate_fund


class FundTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.fund = generate_fund()
        self.asset_id = self.fund.asset_id

    def tearDown(self):
        pass

    def test_Fund(self):
        self.assertEqual(type(self.fund), Fund)

if __name__ == '__main__':
    unittest.main()
