from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.assets.children import Link


class AssetChildrenTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_Link(self):
        """ Currently this test does nothing except check the class can be instantiated """
        link = Link(linked_asset_id='TEST')
        self.assertEqual(type(link), Link)

if __name__ == '__main__':
    unittest.main()
