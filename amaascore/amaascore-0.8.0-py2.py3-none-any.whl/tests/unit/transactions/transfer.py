# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import random
import unittest

from amaascore.assets.interface import AssetsInterface
from amaascore.books.interface import BooksInterface
from amaascore.transactions.interface import TransactionsInterface
from amaascore.transactions.transaction import Transaction
from amaascore.tools.generate_asset import generate_asset
from amaascore.tools.generate_book import generate_book
from amaascore.tools.generate_transaction import generate_transaction
from tests.unit.config import STAGE


class TransferTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.maxDiff = None  # View the complete diff when there is a mismatch in a test
        self.interface = TransactionsInterface(environment=STAGE)
        self.assets_interface = AssetsInterface(environment=STAGE)
        self.books_interface = BooksInterface(environment=STAGE)
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.asset = generate_asset(asset_manager_id=self.asset_manager_id, fungible=True)
        self.trader_one_book = generate_book(asset_manager_id=self.asset_manager_id)
        self.trader_two_book = generate_book(asset_manager_id=self.asset_manager_id)
        self.wash_book = generate_book(asset_manager_id=self.asset_manager_id, book_type='Wash')
        self.setup_cache()

    def setup_cache(self):
        self.create_transaction_asset()
        self.create_transaction_book(self.trader_one_book)
        self.create_transaction_book(self.trader_two_book)
        self.create_transaction_book(self.wash_book)

    def tearDown(self):
        pass

    def create_transaction_asset(self):
        self.assets_interface.upsert(self.asset)

    def create_transaction_book(self, book):
        self.books_interface.new(book)

    def test_BookTransfer(self):
        deliver, receive = self.interface.book_transfer(asset_manager_id=self.asset_manager_id,
                                                        source_book_id=self.trader_one_book.book_id,
                                                        target_book_id=self.trader_two_book.book_id,
                                                        wash_book_id=self.wash_book.book_id,
                                                        asset_id=self.asset.asset_id,
                                                        quantity=100,
                                                        price=Decimal('3.14'),
                                                        currency='USD')
        self.assertEqual(deliver.quantity, 100)
        self.assertEqual(receive.quantity, 100)
        self.assertEqual(deliver.transaction_action, 'Deliver')
        self.assertEqual(receive.transaction_action, 'Receive')
        self.assertEqual(deliver.transaction_type, 'Transfer')
        self.assertEqual(deliver.transaction_type, 'Transfer')
        self.assertEqual(deliver.counterparty_book_id, self.wash_book.book_id)
        self.assertEqual(receive.counterparty_book_id, self.wash_book.book_id)

if __name__ == '__main__':
    unittest.main()
