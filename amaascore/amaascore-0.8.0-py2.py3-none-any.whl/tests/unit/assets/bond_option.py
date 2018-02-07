from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.bond_option import BondOption
from amaascore.tools.generate_asset import generate_bond_option


class BondOptionTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.bond_option = generate_bond_option()
        self.asset_id = self.bond_option.asset_id

    def tearDown(self):
        pass

    def test_BondOption(self):
        self.assertEqual(type(self.bond_option), BondOption)

    def test_Optionality(self):
        self.assertEqual(type(self.bond_option.strike), Decimal)
        self.assertIn(self.bond_option.option_type, ['Put', 'Call'])

if __name__ == '__main__':
    unittest.main()
