from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.assets.sukuk import Sukuk
from amaascore.tools.generate_asset import generate_sukuk


class SukukTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.sukuk = generate_sukuk()
        self.asset_id = self.sukuk.asset_id

    def tearDown(self):
        pass

    def test_Sukuk(self):
        self.assertEqual(type(self.sukuk), Sukuk)

if __name__ == '__main__':
    unittest.main()
