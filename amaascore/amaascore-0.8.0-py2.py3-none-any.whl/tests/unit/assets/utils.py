from __future__ import absolute_import, division, print_function, unicode_literals

import unittest


from amaascore.assets.utils import json_to_asset
from amaascore.tools.generate_asset import generate_asset


class AssetUtilsTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_JsonToAsset(self):
        asset = generate_asset()
        json_asset = asset.to_json()
        gen_asset = json_to_asset(json_asset)
        self.assertEqual(gen_asset, asset)

if __name__ == '__main__':
    unittest.main()
