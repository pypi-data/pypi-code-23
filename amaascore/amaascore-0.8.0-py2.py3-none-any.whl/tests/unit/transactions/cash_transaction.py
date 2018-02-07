from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.transactions.cash_transaction import CashTransaction
from amaascore.tools.generate_transaction import generate_cash_transaction


class CashTransactionTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.transaction = generate_cash_transaction()
        self.transaction_id = self.transaction.transaction_id

    def tearDown(self):
        pass

    def test_Transaction(self):
        self.assertEqual(type(self.transaction), CashTransaction)


if __name__ == '__main__':
    unittest.main()
