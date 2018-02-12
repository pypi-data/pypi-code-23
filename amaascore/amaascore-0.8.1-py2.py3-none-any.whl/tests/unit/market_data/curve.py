from __future__ import absolute_import, division, print_function, unicode_literals

import json
import unittest

from amaascore.market_data.curve import Curve
from amaascore.tools.generate_market_data import generate_curve

class CurveTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.curve = generate_curve()
        self.asset_id = self.curve.asset_id

    def tearDown(self):
        pass

    def test_Curve(self):
        self.assertEqual(type(self.curve), Curve)

    def test_CurveToDict(self):
        curve_dict = self.curve.__dict__
        self.assertEqual(type(curve_dict), dict)
        self.assertEqual(curve_dict.get('asset_id'), self.asset_id)

    def test_CurveToJSON(self):
        curve_json = self.curve.to_json()
        self.assertEqual(curve_json.get('asset_id'), self.asset_id)
        # If party_json is valid JSON, this will run without serialisation errors
        json_asset_id = json.loads(json.dumps(curve_json, ensure_ascii=False)).get('asset_id')
        self.assertEqual(json_asset_id, self.asset_id)

if __name__ == '__main__':
    unittest.main()
