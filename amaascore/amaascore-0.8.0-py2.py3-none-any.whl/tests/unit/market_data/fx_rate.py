from __future__ import absolute_import, division, print_function, unicode_literals

import json
import unittest

from amaascore.market_data.fx_rate import FXRate
from amaascore.tools.generate_market_data import generate_fx_rate


class FXRateTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.fx_rate = generate_fx_rate()
        self.asset_id = self.fx_rate.asset_id

    def tearDown(self):
        pass

    def test_FXRate(self):
        self.assertEqual(type(self.fx_rate), FXRate)

    def test_FXRateToDict(self):
        fx_rate_dict = self.fx_rate.__dict__
        self.assertEqual(type(fx_rate_dict), dict)
        self.assertEqual(fx_rate_dict.get('asset_id'), self.asset_id)

    def test_FXRateToJSON(self):
        fx_rate_json = self.fx_rate.to_json()
        self.assertEqual(fx_rate_json.get('asset_id'), self.asset_id)
        # If party_json is valid JSON, this will run without serialisation errors
        json_asset_id = json.loads(json.dumps(fx_rate_json, ensure_ascii=False)).get('asset_id')
        self.assertEqual(json_asset_id, self.asset_id)

if __name__ == '__main__':
    unittest.main()
