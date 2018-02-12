from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path
import tempfile
import unittest


from amaascore.assets.asset import Asset
from amaascore.assets.utils import json_to_asset
from amaascore.books.book import Book
from amaascore.tools.csv_tools import objects_to_csv, objects_to_csv_stream, \
    csv_filename_to_objects, csv_stream_to_objects
from amaascore.tools.generate_asset import generate_asset
from amaascore.tools.generate_book import generate_book


class CSVTest(unittest.TestCase):
    """ We are using Assets as the example case for testing the generic function"""

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_AssetsToCSV(self):
        filename = os.path.join(tempfile.gettempdir(), 'test.csv')
        assets = [generate_asset() for i in range(5)]
        objects_to_csv(objects=assets, filename=filename, clazz=Asset)
        # Read the file back out again
        with open(filename, 'r') as temp_file:
            data = temp_file.readlines()
        self.assertEqual(len(data), 6)  # 5 assets + header
        os.remove(filename)

    def test_AssetsToCSVStream(self):
        file_desc, temp_filepath = tempfile.mkstemp()
        assets = [generate_asset() for i in range(5)]
        with open(temp_filepath, 'w') as temp_file:
            objects_to_csv_stream(objects=assets, stream=temp_file, clazz=Asset)
        # Read the file back out again
        with open(temp_filepath, 'r') as temp_file:
            data = temp_file.readlines()
        self.assertEqual(len(data), 6)  # 5 assets + header
        os.close(file_desc)
        os.remove(temp_filepath)

    def test_BooksToCSVStream(self):
        # Books have no children so test this case as well.
        file_desc, temp_filepath = tempfile.mkstemp()
        books = [generate_book() for i in range(5)]
        with open(temp_filepath, 'w') as temp_file:
            objects_to_csv_stream(objects=books, stream=temp_file, clazz=Book)
        # Read the file back out again
        with open(temp_filepath, 'r') as temp_file:
            data = temp_file.readlines()
        self.assertEqual(len(data), 6)  # 5 books + header
        os.close(file_desc)
        os.remove(temp_filepath)

    def test_FilenameToAssets(self):
        # Generate file
        filename = os.path.join(tempfile.gettempdir(), 'test.csv')
        assets = [generate_asset() for i in range(5)]
        objects_to_csv(objects=assets, filename=filename, clazz=Asset)
        assets = csv_filename_to_objects(filename, json_handler=json_to_asset)
        self.assertEqual(len(assets), 5)
        self.assertEqual(type(assets[0]), Asset)
        os.remove(filename)

    def test_StreamToAssets(self):
        # Generate file
        filename = os.path.join(tempfile.gettempdir(), 'test.csv')
        assets = [generate_asset() for i in range(5)]
        objects_to_csv(objects=assets, filename=filename, clazz=Asset)
        with open(filename, 'r') as stream:
            assets = csv_stream_to_objects(stream, json_handler=json_to_asset)
        self.assertEqual(len(assets), 5)
        self.assertEqual(type(assets[0]), Asset)
        os.remove(filename)


if __name__ == '__main__':
    unittest.main()
