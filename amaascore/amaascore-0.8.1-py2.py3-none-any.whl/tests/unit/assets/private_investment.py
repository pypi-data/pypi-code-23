from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.assets.private_investment import PrivateInvestment
from amaascore.tools.generate_asset import generate_private_investment


class PrivateInvestmentTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.private_investment = generate_private_investment()
        self.asset_id = self.private_investment.asset_id

    def tearDown(self):
        pass

    def test_PrivateInvestment(self):
        self.assertEqual(type(self.private_investment), PrivateInvestment)

if __name__ == '__main__':
    unittest.main()
