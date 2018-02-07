from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.cryptocurrency import Cryptocurrency
from amaascore.tools.generate_asset import generate_cryptocurrency


class CryptocurrencyTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.crypto = generate_cryptocurrency()
        self.asset_id = self.crypto.asset_id

    def tearDown(self):
        pass

    def test_Cryptocurrency(self):
        self.assertEqual(type(self.crypto), Cryptocurrency)

if __name__ == '__main__':
    unittest.main()
