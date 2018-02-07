# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
from decimal import Decimal
import unittest

from amaascore.assets.interface import AssetsInterface
from amaascore.books.interface import BooksInterface
from amaascore.transactions.children import Charge
from amaascore.transactions.interface import TransactionsInterface
from amaascore.tools.generate_asset import generate_asset
from amaascore.tools.generate_book import generate_book
from amaascore.tools.generate_transaction import generate_transaction
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class AllocationTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.maxDiff = None  # View the complete diff when there is a mismatch in a test
        self.transactions_interface = TransactionsInterface(environment=STAGE)
        self.assets_interface = AssetsInterface(environment=STAGE)
        self.books_interface = BooksInterface(environment=STAGE)
        self.asset_manager_id = 1
        self.asset = generate_asset(asset_manager_id=self.asset_manager_id)
        self.asset_book = generate_book(asset_manager_id=self.asset_manager_id)
        self.counterparty_book = generate_book(asset_manager_id=self.asset_manager_id)
        self.transaction = generate_transaction(asset_manager_id=self.asset_manager_id, asset_id=self.asset.asset_id,
                                                asset_book_id=self.asset_book.book_id,
                                                counterparty_book_id=self.counterparty_book.book_id)
        self.transaction_id = self.transaction.transaction_id
        self.setup_cache()

    def tearDown(self):
        pass

    def create_transaction_asset(self):
        self.assets_interface.upsert(asset)

    def setup_cache(self):
        self.create_transaction_asset()
        self.create_transaction_book(self.asset_book)
        self.create_transaction_book(self.counterparty_book)

    def create_transaction_book(self, book):
        self.books_interface.new(book)

    def test_Allocations(self):
        transaction = generate_transaction(asset_manager_id=self.asset_manager_id, asset_id=self.asset.asset_id,
                                           asset_book_id=self.asset_book.book_id,
                                           counterparty_book_id=self.counterparty_book.book_id,
                                           quantity=Decimal('100'))
        transaction.charges['TEST'] = Charge(charge_value=Decimal('10'), currency='SGD')
        self.transactions_interface.new(transaction)
        allocation_dicts = [{'book_id': 'ABC', 'quantity': Decimal('40')},
                            {'book_id': 'XYZ', 'quantity': Decimal('60')}]
        abc_book = generate_book(asset_manager_id=self.asset_manager_id, book_id='ABC')
        xyz_book = generate_book(asset_manager_id=self.asset_manager_id, book_id='XYZ')
        self.create_transaction_book(abc_book)
        self.create_transaction_book(xyz_book)
        allocations = self.transactions_interface.allocate_transaction(asset_manager_id=self.asset_manager_id,
                                                                       transaction_id=transaction.transaction_id,
                                                                       allocation_type='asset_manager',
                                                                       allocation_dicts=allocation_dicts)
        self.assertEqual(len(allocations), 2)
        book_ids = sorted([allocation.asset_book_id for allocation in allocations])
        self.assertEqual(book_ids, ['ABC', 'XYZ'])
        quantities = sorted([allocation.quantity for allocation in allocations])
        self.assertEqual(quantities, [Decimal('40'), Decimal('60')])
        charges = sorted([allocation.charges.get('TEST').charge_value for allocation in allocations])
        self.assertEqual(charges, [Decimal('4'), Decimal('6')])

    def test_AllocationWithExplictID(self):
        transaction = generate_transaction(asset_manager_id=self.asset_manager_id, asset_id=self.asset.asset_id,
                                           asset_book_id=self.asset_book.book_id,
                                           counterparty_book_id=self.counterparty_book.book_id,
                                           quantity=Decimal('100'))
        self.transactions_interface.new(transaction)
        partial_tran_id = transaction.transaction_id[:10]
        allocation_dicts = [{'book_id': 'ABC', 'quantity': Decimal('60'), 'transaction_id': partial_tran_id + '_ABC'},
                            {'book_id': 'XYZ', 'quantity': Decimal('40'), 'transaction_id': partial_tran_id + '_XYZ'}]
        abc_book = generate_book(asset_manager_id=self.asset_manager_id, book_id='ABC')
        xyz_book = generate_book(asset_manager_id=self.asset_manager_id, book_id='XYZ')
        self.create_transaction_book(abc_book)
        self.create_transaction_book(xyz_book)
        allocations = self.transactions_interface.allocate_transaction(asset_manager_id=self.asset_manager_id,
                                                                       transaction_id=transaction.transaction_id,
                                                                       allocation_type='counterparty',
                                                                       allocation_dicts=allocation_dicts)
        self.assertEqual(len(allocations), 2)
        book_ids = sorted([allocation.counterparty_book_id for allocation in allocations])
        self.assertEqual(book_ids, ['ABC', 'XYZ'])
        quantities = sorted([allocation.quantity for allocation in allocations])
        self.assertEqual(quantities, [Decimal('40'), Decimal('60')])
        transaction_ids = sorted([allocation.transaction_id for allocation in allocations])
        self.assertEqual(transaction_ids, [partial_tran_id + '_ABC', partial_tran_id + '_XYZ'])

    def test_RetrieveTransactionAllocations(self):
        pass

if __name__ == '__main__':
    unittest.main()
