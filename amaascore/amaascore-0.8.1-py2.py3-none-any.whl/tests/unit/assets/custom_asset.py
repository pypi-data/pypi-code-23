from __future__ import absolute_import, division, print_function, unicode_literals

import json
import random
import unittest

from amaascore.assets.custom_asset import CustomAsset
from amaascore.assets.interface import AssetsInterface
from tests.unit.config import STAGE

class Pizza(CustomAsset):

    def __init__(self, size, asset_id, asset_manager_id, toppings=None):
        self.size = size
        self.toppings = toppings
        client_additional = json.dumps({'size': self.size, 'toppings': self.toppings})
        super(Pizza, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                    client_additional=client_additional, fungible=False)


class CustomAssetTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        asset_manager_id = random.randint(1, 2**31-1)
        self.pizza = Pizza(asset_id='pizza1', asset_manager_id=asset_manager_id,
                           size='Large', toppings=['pineapple', 'corn', 'garlic'])
        self.assets_interface = AssetsInterface(environment=STAGE)

    def tearDown(self):
        pass

    def test_CustomAsset(self):
        pizza = self.assets_interface.new(self.pizza)
        self.assertEqual(type(pizza), CustomAsset)
        self.assertIsNotNone(pizza.client_additional)

if __name__ == '__main__':
    unittest.main()
