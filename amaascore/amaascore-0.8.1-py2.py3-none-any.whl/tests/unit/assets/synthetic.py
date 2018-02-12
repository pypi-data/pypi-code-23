from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.synthetic import Synthetic
from amaascore.tools.generate_asset import generate_synthetic


class SyntheticTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.synthetic = generate_synthetic()
        self.asset_id = self.synthetic.asset_id

    def tearDown(self):
        pass

    def test_Synthetic(self):
        self.assertEqual(type(self.synthetic), Synthetic)

if __name__ == '__main__':
    unittest.main()
