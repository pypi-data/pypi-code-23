from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.assets.warrants import Warrant
from amaascore.tools.generate_asset import generate_warrant


class PrivateInvestmentTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.warrant = generate_warrant()
        self.asset_id = self.warrant.asset_id

    def tearDown(self):
        pass

    def test_PrivateInvestment(self):
        self.assertEqual(type(self.warrant), Warrant)

if __name__ == '__main__':
    unittest.main()
