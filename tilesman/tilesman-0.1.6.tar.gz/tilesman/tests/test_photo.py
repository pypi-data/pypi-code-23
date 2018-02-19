import os
import re
import unittest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tilesman.tests.helpers.image_handling as ih
import tilesman.tests.helpers.file_system as fs
from tilesman.photo import *


test_dir = os.path.join('.', 'test_tmp')
test_image_path = os.path.join(test_dir, 'test_image.jpg')
tiles_dir = 'extrated_tiles'

class TestPhotoMethods(unittest.TestCase):
	'''
	Unit tests for the photo module
	'''

	def setUp(self):
		fs.create_dir(test_dir)
		ih.mock_image_on_file_system(test_image_path, 875, 625)

	def tearDown(self):
		fs.delete_dir(test_dir)
	
	def test_photo_init_exception(self):
		with self.assertRaises(InputFileException):
			Photo(os.path.join(test_dir, 'fake_test_image.jpg'))

	def test_photo_init(self):
		img = Photo(test_image_path)
		self.assertEqual(img.path, test_image_path)
		self.assertEqual((img.width, img.height), (875, 625))
		self.assertEqual(img.file_format, 'jpg')

	def test_extract_tiles_exception(self):
		img = Photo(test_image_path)
		with self.assertRaises(TilingException):
			img.extract_tiles(tiles_dir, 0, 0)

	def test_extract_tiles(self):
		img = Photo(test_image_path)
		img.extract_tiles(tiles_dir, 256, 256)
		tiles_dir_path = os.path.join(test_dir, tiles_dir)

		# Get all extratec tiles by file name
		tile_paths = fs.scan_dir(tiles_dir_path, 'file')

		# Checking tile count
		self.assertEqual(len(tile_paths), 12)
		
		# Check if all tiles in row y = 0 make up the same width of the original image
		self.assertEqual(
			sum([ih.load_image(os.path.join(tiles_dir_path, path)).size[0] for path in tile_paths if re.compile('\d_0\.jpg$').match(path)]), 875
		)
		# Check if all tiles in column x = 0 make up the same height of the original image
		self.assertEqual(
			sum([ih.load_image(os.path.join(tiles_dir_path, path)).size[1] for path in tile_paths if re.compile('0_\d\.jpg$').match(path)]), 625
		)

	def test_shrink_exception(self):
		img = Photo(test_image_path)
		with self.assertRaises(InvalidResizingException):
			img.shrink(-1)

	def test_shrink(self):
		img = Photo(test_image_path)
		img.shrink(0.5)
		self.assertEqual(img.width, 438)
		self.assertEqual(img.height, 313)
