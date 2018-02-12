from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.transactions.utils import json_to_transaction, json_to_position
from amaascore.tools.generate_transaction import generate_transaction, generate_position


class TransactionUtilsTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_JsonToTransaction(self):
        transaction = generate_transaction()
        json_transaction = transaction.to_json()
        gen_transaction = json_to_transaction(json_transaction)
        self.assertEqual(gen_transaction, transaction)

    def test_JsonToPosition(self):
        position = generate_position()
        json_position = position.to_json()
        gen_position = json_to_position(json_position)
        self.assertEqual(gen_position, position)

if __name__ == '__main__':
    unittest.main()
