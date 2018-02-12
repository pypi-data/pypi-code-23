from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.assets.automobile import Automobile
from amaascore.tools.generate_asset import generate_automobile


class AutomobileTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.automobile = generate_automobile()
        self.asset_id = self.automobile.asset_id

    def tearDown(self):
        pass

    def test_Automobile(self):
        self.assertEqual(type(self.automobile), Automobile)

if __name__ == '__main__':
    unittest.main()
