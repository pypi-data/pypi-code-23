from __future__ import absolute_import, division, print_function, unicode_literals

import random
import unittest

from amaascore.assets.future import Future
from amaascore.assets.interface import AssetsInterface
from amaascore.tools.generate_asset import generate_future
from tests.unit.config import STAGE

class FutureTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.maxDiff = None
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.future = generate_future(asset_manager_id=self.asset_manager_id)
        self.asset_id = self.future.asset_id
        self.assets_interface = AssetsInterface(environment=STAGE)

    def tearDown(self):
        pass

    def test_Future(self):
        self.assertEqual(type(self.future), Future)
        self.assertEqual(self.future.pricing_method(), 'Market')

    def test_Persistence(self):
        self.assets_interface.new(self.future)
        future = self.assets_interface.retrieve(asset_manager_id=self.asset_manager_id, asset_id=self.asset_id)
        self.assertEqual(future, self.future)

if __name__ == '__main__':
    unittest.main()
