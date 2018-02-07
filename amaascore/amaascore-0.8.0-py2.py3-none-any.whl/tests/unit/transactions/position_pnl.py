from __future__ import absolute_import, division, print_function, unicode_literals
from decimal import Decimal
import json
import unittest

from amaascore.transactions.position_pnl import PositionPNL
from amaascore.tools.generate_transaction import generate_position_pnl


class PositiontionPNLTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.position_pnl = generate_position_pnl()

    def tearDown(self):
        pass

    def test_PositionPNL(self):
        self.assertEqual(type(self.position_pnl), PositionPNL)

    def test_PNLPeriodEnum(self):
        with self.assertRaisesRegexp(ValueError, 'Unrecognized PnL period'):
            self.position_pnl.period = 'year to date'

    def test_PositionPNLToDict(self):
        position_pnl_dict = self.position_pnl.to_dict()
        self.assertEqual(type(position_pnl_dict), dict)
        self.assertEqual(position_pnl_dict.get('total_pnl'), self.position_pnl.total_pnl)

    def test_PositionPNLToJSON(self):
        position_pnl_json = self.position_pnl.to_json()
        self.assertEqual(Decimal(position_pnl_json.get('total_pnl')), self.position_pnl.total_pnl)
        json_total_pnl = Decimal(json.loads(json.dumps(position_pnl_json, ensure_ascii=False)).get('total_pnl'))
        self.assertEqual(json_total_pnl, self.position_pnl.total_pnl)


if __name__ == '__main__':
    unittest.main()
