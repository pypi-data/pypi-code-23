from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.assets.wine import Wine
from amaascore.tools.generate_real_asset import generate_wine


class WineTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.wine = generate_wine()
        self.asset_id = self.wine.asset_id

    def tearDown(self):
        pass

    def test_Wine(self):
        self.assertEqual(type(self.wine), Wine)

if __name__ == '__main__':
    unittest.main()
