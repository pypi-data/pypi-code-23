from __future__ import absolute_import, division, print_function, unicode_literals

import json
import unittest

from amaascore.market_data.eod_price import EODPrice
from amaascore.tools.generate_market_data import generate_eod_price


class EODPriceTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.eod_price = generate_eod_price()
        self.asset_id = self.eod_price.asset_id

    def tearDown(self):
        pass

    def test_EODPrice(self):
        self.assertEqual(type(self.eod_price), EODPrice)

    def test_EODPriceToDict(self):
        eod_price_dict = self.eod_price.__dict__
        self.assertEqual(type(eod_price_dict), dict)
        self.assertEqual(eod_price_dict.get('asset_id'), self.asset_id)

    def test_EODPriceToJSON(self):
        eod_price_json = self.eod_price.to_json()
        self.assertEqual(eod_price_json.get('asset_id'), self.asset_id)
        # If party_json is valid JSON, this will run without serialisation errors
        json_asset_id = json.loads(json.dumps(eod_price_json, ensure_ascii=False)).get('asset_id')
        self.assertEqual(json_asset_id, self.asset_id)

if __name__ == '__main__':
    unittest.main()
