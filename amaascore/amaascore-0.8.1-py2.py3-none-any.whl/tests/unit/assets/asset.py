from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.tools.generate_asset import generate_asset
from amaascore.tools.generate_asset import generate_bond


class AssetTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_AssetTypeDisplay(self):
        asset = generate_asset()
        bond = generate_bond()
        self.assertEqual(asset.asset_type_display, 'Asset')
        self.assertEqual(bond.asset_type_display, 'Bond Government')
        self.assertEqual(asset.pricing_method(), 'Derived')
        self.assertEqual(bond.pricing_method(), 'Derived')

if __name__ == '__main__':
    unittest.main()
