# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.assets.interface import AssetsInterface
from amaascore.books.interface import BooksInterface
from amaascore.transactions.interface import TransactionsInterface
from amaascore.transactions.transaction import Transaction
from amaascore.tools.generate_asset import generate_asset
from amaascore.tools.generate_book import generate_book
from amaascore.tools.generate_transaction import generate_transaction
from tests.unit.config import STAGE


class NettingTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.maxDiff = None  # View the complete diff when there is a mismatch in a test
        self.interface = TransactionsInterface(environment=STAGE)
        self.asset_manager_id = 1
        self.assets_interface = AssetsInterface(environment=STAGE)
        self.books_interface = BooksInterface(environment=STAGE)
        self.asset = generate_asset(asset_manager_id=self.asset_manager_id, fungible=True)
        self.asset_book = generate_book(asset_manager_id=self.asset_manager_id)
        self.counterparty_book = generate_book(asset_manager_id=self.asset_manager_id, book_type='Counterparty')
        self.transaction1 = generate_transaction(asset_manager_id=self.asset_manager_id, asset_id=self.asset.asset_id,
                                                 asset_book_id=self.asset_book.book_id,
                                                 counterparty_book_id=self.counterparty_book.book_id,
                                                 transaction_currency='USD',
                                                 net_affecting_charges=True,
                                                 charge_currency='USD')
        self.transaction2 = generate_transaction(asset_manager_id=self.asset_manager_id, asset_id=self.asset.asset_id,
                                                 asset_book_id=self.asset_book.book_id,
                                                 counterparty_book_id=self.counterparty_book.book_id,
                                                 transaction_currency='USD',
                                                 net_affecting_charges=True,
                                                 charge_currency='USD')
        self.setup_cache()
        self.interface.new(self.transaction1)
        self.interface.new(self.transaction2)
        self.transaction_id1 = self.transaction1.transaction_id
        self.transaction_id2 = self.transaction2.transaction_id

    def tearDown(self):
        pass

    def create_transaction_asset(self):
        self.assets_interface.upsert(self.asset)

    def setup_cache(self):
        self.create_transaction_asset()
        self.create_transaction_book(self.asset_book)
        self.create_transaction_book(self.counterparty_book)

    def create_transaction_book(self, book):
        self.books_interface.new(book)

    def test_GenerateNettingSet(self):
        net = self.interface.net_transactions(asset_manager_id=self.asset_manager_id,
                                              transaction_ids=[self.transaction_id1, self.transaction_id2])
        self.assertEqual(type(net), Transaction)
        transaction_ids = {link.linked_transaction_id for link in net.links.get('NettingSet')}
        self.assertEqual(transaction_ids, {self.transaction_id1, self.transaction_id2})

    def test_RetrieveNettingSet(self):
        net = self.interface.net_transactions(asset_manager_id=self.asset_manager_id,
                                              transaction_ids=[self.transaction_id1, self.transaction_id2])
        net_transaction_id, netting_set = self.interface.retrieve_netting_set(asset_manager_id=self.asset_manager_id,
                                                                              transaction_id=net.transaction_id)
        self.assertEqual(net_transaction_id, net.transaction_id)
        self.assertEqual(len(netting_set), 2)
        transaction_ids = {transaction.transaction_id for transaction in netting_set}
        self.assertEqual(transaction_ids, {self.transaction_id1, self.transaction_id2})

if __name__ == '__main__':
    unittest.main()
