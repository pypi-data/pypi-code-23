import os
import unittest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tilesman.tests.helpers.image_handling as ih
import tilesman.tests.helpers.file_system as fs
from tilesman.tile import *


test_dir = os.path.join('.', 'test_tmp')

class TestTileMethods(unittest.TestCase):
	'''
	Unit tests for the tile module
	'''

	def setUp(self):
		fs.create_dir(test_dir)

	def tearDown(self):
		fs.delete_dir(test_dir)

	def test_object_init(self):
		tile_binary = ih.mock_image_on_memory(400, 200)
		tile = Tile(tile_binary, (2, 4), 'jpg')
		self.assertEqual((tile.width, tile.height), (400, 200))
		self.assertEqual(tile.coordinates, (2, 4))
		self.assertEqual(tile.file_format, 'jpg')

	def test_save(self):
		tile_binary = ih.mock_image_on_memory(250, 500)
		tile = Tile(tile_binary, (2, 4), 'jpg')
		tile.save(test_dir)

		expected_tile_path = os.path.join(test_dir, '2_4.jpg')
		self.assertTrue(os.path.isfile(expected_tile_path))

		img = ih.load_image(expected_tile_path)
		self.assertEqual(img.size, (250, 500))

		os.remove(expected_tile_path)
