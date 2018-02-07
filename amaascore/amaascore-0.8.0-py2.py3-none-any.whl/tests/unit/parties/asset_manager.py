from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.parties.asset_manager import AssetManager
from amaascore.tools.generate_party import generate_asset_manager


class AssetManagerTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager = generate_asset_manager()
        self.party_id = self.asset_manager.party_id

    def tearDown(self):
        pass

    def test_AssetManager(self):
        self.assertEqual(type(self.asset_manager), AssetManager)

if __name__ == '__main__':
    unittest.main()
