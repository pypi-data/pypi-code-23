from __future__ import absolute_import, division, print_function, unicode_literals

import random
import unittest

from amaascore.assets.bond import BondGovernment
from amaascore.assets.interface import AssetsInterface
from amaascore.tools.generate_asset import generate_bond
from tests.unit.config import STAGE

class BondTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.bond = generate_bond(asset_manager_id=self.asset_manager_id)
        self.asset_id = self.bond.asset_id
        self.assets_interface = AssetsInterface(environment=STAGE)

    def tearDown(self):
        pass

    def test_Bond(self):
        self.assertEqual(type(self.bond), BondGovernment)

    def test_Persistence(self):
        self.assets_interface.new(self.bond)
        bond = self.assets_interface.retrieve(asset_manager_id=self.asset_manager_id, asset_id=self.asset_id)
        self.assertEqual(bond, self.bond)

if __name__ == '__main__':
    unittest.main()
