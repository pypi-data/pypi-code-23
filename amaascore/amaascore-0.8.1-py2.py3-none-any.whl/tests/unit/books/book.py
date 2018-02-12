from __future__ import absolute_import, division, print_function, unicode_literals

import copy
import json
import unittest

from amaascore.books.book import Book
from amaascore.tools.generate_book import generate_book


class BookTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.book = generate_book()
        self.book_id = self.book.book_id

    def tearDown(self):
        pass

    def test_Book(self):
        self.assertEqual(type(self.book), Book)

    def test_BookToDict(self):
        # TODO - add a to_dict function?
        book_dict = self.book.__dict__
        self.assertEqual(type(book_dict), dict)
        self.assertEqual(book_dict.get('book_id'), self.book_id)

    def test_BookToJSON(self):
        book_json = self.book.to_json()
        self.assertEqual(book_json.get('book_id'), self.book_id)
        # If book_json is valid JSON, this will run without serialisation errors
        json_book_id = json.loads(json.dumps(book_json, ensure_ascii=False)).get('book_id')
        self.assertEqual(json_book_id, self.book_id)

    def test_BookEquality(self):
        book2 = copy.deepcopy(self.book)
        book3 = copy.deepcopy(self.book)
        book3.book_status = 'Retired'
        self.assertEqual(self.book, book2)
        self.assertEqual(len({self.book, book2}), 1)
        self.assertEqual(len({self.book, book3}), 2)
        self.assertNotEqual(self.book, book3)

    def test_InvalidBookType(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid book type Invalid'):
            book = generate_book(book_type='Invalid')

if __name__ == '__main__':
    unittest.main()
