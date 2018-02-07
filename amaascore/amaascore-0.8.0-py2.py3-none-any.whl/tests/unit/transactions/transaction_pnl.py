from __future__ import absolute_import, division, print_function, unicode_literals
from decimal import Decimal
import json
import unittest

from amaascore.transactions.transaction_pnl import TransactionPNL
from amaascore.tools.generate_transaction import generate_transaction_pnl


class TransactionPNLTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.transaction_pnl = generate_transaction_pnl()

    def tearDown(self):
        pass

    def test_TransactionPNL(self):
        self.assertEqual(type(self.transaction_pnl), TransactionPNL)

    def test_PNLPeriodEnum(self):
        with self.assertRaisesRegexp(ValueError, 'Unrecognized PnL period'):
            self.transaction_pnl.period = 'year to date'

    def test_TransactionPNLToDict(self):
        transaction_pnl_dict = self.transaction_pnl.to_dict()
        self.assertEqual(type(transaction_pnl_dict), dict)
        self.assertEqual(transaction_pnl_dict.get('total_pnl'), self.transaction_pnl.total_pnl)

    def test_TransactionPNLToJSON(self):
        transaction_pnl_json = self.transaction_pnl.to_json()
        self.assertEqual(Decimal(transaction_pnl_json.get('total_pnl')), self.transaction_pnl.total_pnl)
        json_total_pnl = Decimal(json.loads(json.dumps(transaction_pnl_json, ensure_ascii=False)).get('total_pnl'))
        self.assertEqual(json_total_pnl, self.transaction_pnl.total_pnl)

    def test_TransactionPNLAdditional(self):
        test_dict = {'a': 1, 'b': '2'}
        pnl = generate_transaction_pnl(additional=test_dict, error_message='[Error]')
        self.assertDictEqual(pnl.additional, test_dict)
        self.assertEqual(pnl.error_message, '[Error]')


if __name__ == '__main__':
    unittest.main()
