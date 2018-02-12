from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import random
import unittest

from amaascore.assets.foreign_exchange import (
    ForeignExchange, ForeignExchangeForward, ForeignExchangeSpot,
    calculate_rates,
)
from amaascore.assets.interface import AssetsInterface
from amaascore.tools.generate_asset import generate_foreignexchange, generate_fx_forward, generate_fx_spot
from tests.unit.config import STAGE


class ForeignExchangeTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.fx_forward = generate_fx_forward(asset_manager_id=self.asset_manager_id)
        self.asset_id = self.fx_forward.asset_id
        self.assets_interface = AssetsInterface(environment=STAGE)

    def tearDown(self):
        pass

    def test_ForeignExchange(self):
        fx = generate_foreignexchange(asset_id='USDJPY')
        self.assertEqual(type(fx), ForeignExchange)
        self.assertEqual(self.fx_forward.pricing_method(), 'Derived')

    def test_ForeignExchangeForward(self):
        self.assertEqual(type(self.fx_forward), ForeignExchangeForward)

    def test_ForeignExchangeSpot(self):
        fx_spot = generate_fx_spot(asset_manager_id=self.asset_manager_id)
        self.assertEqual(type(fx_spot), ForeignExchangeSpot)

    def test_Persistence(self):
        self.assets_interface.new(self.fx_forward)
        fx_forward = self.assets_interface.retrieve(asset_manager_id=self.asset_manager_id, asset_id=self.asset_id)
        self.assertEqual(fx_forward, self.fx_forward)

    def test_rates(self):
        examples = [
            (('SGD', 'USD'),
             {'forward_rate': Decimal('1.354'), 'spot_reference': Decimal('1.356')},
             {'fwd_points': Decimal('-20')}),
            (('SGD', 'USD'),
             {'spot_reference': Decimal('1.356'), 'fwd_points': Decimal('-20')},
             {'forward_rate': Decimal('1.354')}),
            (('SGD', 'USD'),
             {'forward_rate': Decimal('1.354'), 'fwd_points': Decimal('-20')},
             {'spot_reference': Decimal('1.356')}),
        ]
        for a, kw, expect in examples:
            expect.update(kw)
            result = calculate_rates(*a, **kw)
            self.assertEqual(result, expect)


if __name__ == '__main__':
    unittest.main()
