from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.bond_option import BondOption
from amaascore.tools.generate_asset import generate_bond_option


class OptionMixinTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        # We're using a bond option as an example option, but all tested functionality is from the mixin
        self.bond_option = generate_bond_option()
        self.asset_id = self.bond_option.asset_id

    def tearDown(self):
        pass

    def test_InvalidStyle(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid value for option_style: Invalid'):
            self.bond_option.option_style = 'Invalid'

    def test_InvalidType(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid value for option_type: Invalid'):
            self.bond_option.option_type = 'Invalid'

if __name__ == '__main__':
    unittest.main()
