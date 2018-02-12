from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.tools.generate_asset_manager import generate_asset_manager


class AssetManagerTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager = generate_asset_manager()

    def tearDown(self):
        pass

    def test_AssetManagerType(self):
        with self.assertRaisesRegexp(ValueError, 'Asset Manager Type: INVALID is invalid.'):
            self.asset_manager.asset_manager_type = 'INVALID'

    def test_AccountType(self):
        with self.assertRaisesRegexp(ValueError, 'Account Type: INVALID is invalid.'):
            self.asset_manager.account_type = 'INVALID'

if __name__ == '__main__':
    unittest.main()
