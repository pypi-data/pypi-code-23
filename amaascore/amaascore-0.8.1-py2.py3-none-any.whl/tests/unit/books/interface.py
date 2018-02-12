# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
import random
import unittest

from amaascore.books.interface import BooksInterface
from amaascore.tools.generate_book import generate_book
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class BooksInterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.books_interface = BooksInterface(environment=STAGE)
        cls.asset_manager_id = random.randint(1, 2**31-1)

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.book = generate_book(asset_manager_id=self.asset_manager_id)
        self.book_id = self.book.book_id

    def tearDown(self):
        pass

    def test_New(self):
        self.assertIsNone(self.book.created_time)
        book = self.books_interface.new(self.book)
        # TODO - this should be populated by the New call.
        #self.assertIsNotNone(book.created_time)
        self.assertEqual(book.book_id, self.book_id)

    def test_Amend(self):
        book = self.books_interface.new(self.book)
        self.assertEqual(book.version, 1)
        book.owner_id = 'TEST'
        book = self.books_interface.amend(book)
        self.assertEqual(book.owner_id, 'TEST')
        self.assertEqual(book.version, 2)

    def test_Retrieve(self):
        self.books_interface.new(self.book)
        book = self.books_interface.retrieve(self.book.asset_manager_id, self.book.book_id)
        self.assertEqual(book.book_id, self.book_id)

    def test_Retire(self):
        self.books_interface.new(self.book)
        self.books_interface.retire(self.book.asset_manager_id, self.book.book_id)
        book = self.books_interface.retrieve(self.book.asset_manager_id, self.book.book_id)
        self.assertEqual(book.book_id, self.book_id)
        self.assertEqual(book.book_status, 'Retired')

    def test_Search(self):
        all_books = self.books_interface.search(self.asset_manager_id)
        random_book_index = random.randint(0, len(all_books)-1)
        asset_manager_id = all_books[random_book_index].asset_manager_id
        asset_manager_books = [book for book in all_books if book.asset_manager_id == asset_manager_id]
        books = self.books_interface.search(asset_manager_id=asset_manager_id)
        self.assertEqual(len(books), len(asset_manager_books))

    def test_BookConfigByAssetManager(self):
        book = generate_book()
        self.books_interface.new(book)
        book_config = self.books_interface.book_config(asset_manager_id=book.asset_manager_id)
        self.assertEqual(len(book_config.keys()), 3)
        self.assertEqual(len(book_config.get('business_unit')), 1)
        self.assertEqual(len(book_config.get('owner_id')), 1)
        self.assertEqual(len(book_config.get('party_id')), 1)

    def test_Unicode(self):
        unicode_description = '日本語入力'
        self.book.description = unicode_description
        book = self.books_interface.new(self.book)
        self.assertEqual(book.description, unicode_description)

    def test_Clear(self):
        self.books_interface.new(self.book)
        count = self.books_interface.clear(self.asset_manager_id)
        self.assertEqual(count, 1)
        results = self.books_interface.search(asset_manager_id=self.asset_manager_id)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
