from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import random
import unittest

from amaascore.assets.fx_option import ForeignExchangeOption
from amaascore.assets.interface import AssetsInterface
from amaascore.tools.generate_asset import generate_fx_option
from tests.unit.config import STAGE


class ForeignExchangeOptionTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.fx_option = generate_fx_option(asset_manager_id=self.asset_manager_id)
        self.asset_id = self.fx_option.asset_id
        self.assets_interface = AssetsInterface(environment=STAGE)

    def tearDown(self):
        pass

    def test_ForeignExchangeOption(self):
        self.assertEqual(type(self.fx_option), ForeignExchangeOption)

    def test_Optionality(self):
        self.assertEqual(type(self.fx_option.strike), Decimal)
        self.assertIn(self.fx_option.option_type, ['Put', 'Call'])

    def test_Persistence(self):
        self.assets_interface.new(self.fx_option)
        fx_option = self.assets_interface.retrieve(asset_manager_id=self.asset_manager_id, asset_id=self.asset_id)
        self.assertEqual(fx_option, self.fx_option)

if __name__ == '__main__':
    unittest.main()
