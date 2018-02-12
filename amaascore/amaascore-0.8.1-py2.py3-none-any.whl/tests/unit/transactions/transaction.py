from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
import copy
import json
import unittest

from amaascore.exceptions import TransactionNeedsSaving
from amaascore.transactions.children import Link, Party
from amaascore.transactions.transaction import Transaction
from amaascore.tools.generate_transaction import generate_transaction, REFERENCE_TYPES


class TransactionTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.transaction = generate_transaction(net_affecting_charges=True)
        self.transaction_id = self.transaction.transaction_id

    def tearDown(self):
        pass

    def test_Transaction(self):
        self.assertEqual(type(self.transaction), Transaction)

    def test_ChargesNetEffect(self):
        """
        Long-winded approach as the shorter sum based approach is used in the Transaction class
        :return:
        """
        total = 0
        for charge in self.transaction.charges.values():
            if charge.net_affecting:
                total += charge.charge_value
        self.assertEqual(self.transaction.charges_net_effect(), total)

    def test_TransactionNetSettlement(self):
        """
        Long-winded approach as the shorter sum based approach is used in the Transaction class
        :return:
        """
        total = 0
        for charge in self.transaction.charges.values():
            if charge.net_affecting:
                total += charge.charge_value
        self.assertEqual(self.transaction.net_settlement, self.transaction.gross_settlement - total)

    def test_TransactionToDict(self):
        transaction_dict = self.transaction.__dict__
        self.assertEqual(type(transaction_dict), dict)
        self.assertEqual(transaction_dict.get('transaction_id'), self.transaction_id)
        self.assertEqual(type(transaction_dict.get('charges')), dict)

    def test_TransactionToJSON(self):
        transaction_json = self.transaction.to_json()
        self.assertEqual(transaction_json.get('transaction_id'), self.transaction_id)
        # If transaction_json is valid JSON, this will run without serialisation errors
        json_transaction_id = json.loads(json.dumps(transaction_json, ensure_ascii=False)).get('transaction_id')
        self.assertEqual(json_transaction_id, self.transaction_id)

    def test_TransactionPostings(self):
        with self.assertRaises(TransactionNeedsSaving):
            self.transaction.postings
        # TODO - Save the transaction, and check that the postings are now present

    def test_TransactionEquality(self):
        transaction2 = copy.deepcopy(self.transaction)
        transaction3 = copy.deepcopy(self.transaction)
        transaction3.transaction_status = 'Cancelled'
        self.assertEqual(self.transaction, transaction2)
        self.assertEqual(len({self.transaction, transaction2}), 1)
        self.assertEqual(len({self.transaction, transaction3}), 2)
        self.assertNotEqual(self.transaction, transaction3)

    def test_References(self):
        self.assertEqual(len(self.transaction.references), len(REFERENCE_TYPES) + 1,
                         "AMaaS Reference + the ones added by the transaction generator")
        self.assertEqual(self.transaction.references.get('AMaaS').reference_value, self.transaction.transaction_id)

    def test_MultipleLink(self):
        links = self.transaction.links.get('Multiple')
        self.assertEqual(len(links), 3)  # The test script inserts 3 links

    def test_UpsertLinkList(self):
        links = self.transaction.links.get('Multiple')
        random_id = random_string(8)
        links.add(Link(linked_transaction_id=random_id))
        self.transaction.upsert_link_set('Multiple', links)
        links = self.transaction.links.get('Multiple')
        self.assertEqual(len(links), 4)  # The test script inserts 3 links
        random_id_link = [link for link in links if link.linked_transaction_id == random_id]
        self.assertEqual(len(random_id_link), 1)

    def test_UpsertLinkListEmptyValue(self):
        self.transaction.upsert_link_set('Single', None)
        self.assertEqual(self.transaction.links.get('Single', 'DUMMY'), 'DUMMY')
        # Try to upsert a link_list which isn't present
        self.transaction.upsert_link_set('TEST', None)

    def test_AddLink(self):
        # Add to a Single item
        random_id = random_string(8)
        self.transaction.add_link(link_type='Single', linked_transaction_id=random_id)
        links = self.transaction.links.get('Single')
        self.assertEqual(len(links), 2)  # The test script inserts 1 link
        random_id_link = [link for link in links if link.linked_transaction_id == random_id]
        self.assertEqual(len(random_id_link), 1)
        # Add to a multiple item
        self.transaction.add_link(link_type='Multiple', linked_transaction_id=random_id)
        links = self.transaction.links.get('Multiple')
        self.assertEqual(len(links), 4)  # The test script inserts 3 links
        random_id_link = [link for link in links if link.linked_transaction_id == random_id]
        self.assertEqual(len(random_id_link), 1)
        # Add brand new item
        self.transaction.add_link(link_type='TEST', linked_transaction_id=random_id)
        link = self.transaction.links.get('TEST')
        self.assertEqual(type(link), Link)  # The test script inserts 3 links
        self.assertEqual(link.linked_transaction_id, random_id)

    def test_RemoveLink(self):
        # Remove a single link
        single_id = self.transaction.links.get('Single').linked_transaction_id
        self.transaction.remove_link(link_type='Single', linked_transaction_id=single_id)
        self.assertEqual(self.transaction.links.get('Single', 'DUMMY'), 'DUMMY')
        # Remove a multiple link
        multiple_id = next(iter(self.transaction.links.get('Multiple'))).linked_transaction_id
        self.transaction.remove_link(link_type='Multiple', linked_transaction_id=multiple_id)
        multiple = self.transaction.links.get('Multiple')
        self.assertEqual(len(multiple), 2)  # Test originally added 3
        multiple_id_link = [link for link in multiple if link.linked_transaction_id == multiple_id]
        self.assertEqual(len(multiple_id_link), 0)
        # Remove a link_type that doesn't exist
        with self.assertRaisesRegexp(KeyError, 'Cannot remove link'):
            self.transaction.remove_link('TEST', '1234')
        # Remove a link that doesn't exist
        with self.assertRaisesRegexp(KeyError, 'Cannot remove link'):
            self.transaction.remove_link('Multiple', '1234')

    def test_InvalidTransactionType(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid transaction type Invalid'):
            transaction = generate_transaction(transaction_type='Invalid')

    def test_InvalidTransactionAction(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid transaction action Invalid'):
            transaction = generate_transaction(transaction_action='Invalid')

    def test_InvalidTransactionStatus(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid transaction status Invalid'):
            transaction = generate_transaction(transaction_status='Invalid')

    def test_ImmutableDicts(self):
        attr = self.transaction.to_dict()
        attr.pop('parties')  # Remove parties so that the default constructor is used
        transaction = Transaction(**attr)
        transaction.parties.update({'TEST': Party(party_id=random_string(8))})
        self.assertEqual(len(transaction.parties), 1)
        transaction2 = Transaction(**attr)
        self.assertEqual(len(transaction2.parties), 0)

    def test_InvalidCurrency(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid currency Invalid'):
            self.transaction.transaction_currency = 'Invalid'

if __name__ == '__main__':
    unittest.main()
