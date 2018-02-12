from __future__ import absolute_import, division, print_function, unicode_literals
from decimal import Decimal
import json
import unittest

from amaascore.transactions.book_report import BookReport
from amaascore.tools.generate_transaction import generate_book_report


class BookReportTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.book_report = generate_book_report()

    def tearDown(self):
        pass

    def test_BookReport(self):
        self.assertEqual(type(self.book_report), BookReport)

    def test_BookReportToDict(self):
        book_report_dict = self.book_report.to_dict()
        self.assertEqual(type(book_report_dict), dict)
        self.assertEqual(book_report_dict.get('mtm_value'), self.book_report.mtm_value)

    def test_BookReportToJSON(self):
        book_report_json = self.book_report.to_json()
        self.assertEqual(Decimal(book_report_json.get('mtm_value')), self.book_report.mtm_value)
        mtm_value = Decimal(json.loads(json.dumps(book_report_json, ensure_ascii=False)).get('mtm_value'))
        self.assertEqual(mtm_value, self.book_report.mtm_value)

if __name__ == '__main__':
    unittest.main()
