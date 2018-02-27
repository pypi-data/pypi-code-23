import os
import re
import unittest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tilesman.tests.helpers.image_handling as ih
import tilesman.tests.helpers.file_system as fs
from tilesman.photo import *


TEST_DIR_PATH = os.path.join('.', 'test_tmp')
TEST_IMAGE_NAME = 'test_image'
TEST_IMAGE_FORMAT = 'jpg'
TEST_IMAGE_PATH = os.path.join(TEST_DIR_PATH, '.'.join([TEST_IMAGE_NAME, TEST_IMAGE_FORMAT]))
IMAGE_TILES_DIR_PATH = os.path.join(TEST_DIR_PATH, 'tiles', TEST_IMAGE_NAME)
IMAGE_TILING_LEVEL_NAME = 'tiling_level'

class TestPhotoMethods(unittest.TestCase):
	'''
	Unit tests for the photo module
	'''

	def setUp(self):
		fs.create_dir(TEST_DIR_PATH)
		ih.mock_image_file(TEST_IMAGE_PATH, 875, 625)

	def tearDown(self):
		fs.delete_dir(TEST_DIR_PATH)
	
	def test_photo_init_exception(self):
		with self.assertRaises(OSError):
			Photo(os.path.join(TEST_DIR_PATH, 'fake_test_image.jpg'))

	def test_photo_init(self):
		img = Photo(TEST_IMAGE_PATH)
		self.assertEqual(img.dir, TEST_DIR_PATH)
		self.assertEqual(img.name, TEST_IMAGE_NAME)
		self.assertEqual(img.file_format, TEST_IMAGE_FORMAT)
		self.assertEqual([img.width, img.height], [875, 625])

	def test_extract_tiles_exception(self):
		img = Photo(TEST_IMAGE_PATH)
		with self.assertRaises(ZeroDivisionError):
			img.extract_tiles(IMAGE_TILING_LEVEL_NAME, 0, 0)

	def test_extract_tiles(self):
		img = Photo(TEST_IMAGE_PATH)
		img.extract_tiles(IMAGE_TILING_LEVEL_NAME, 256, 256)

		# Get all extratec tiles by file name
		tile_dir_path = os.path.join(IMAGE_TILES_DIR_PATH, IMAGE_TILING_LEVEL_NAME)
		tile_names = fs.scan_dir(tile_dir_path, 'file')

		# Checking tile count
		self.assertEqual(len(tile_names), 12)
		
		# Check if all tiles in row y = 0 make up the same width of the original image
		self.assertEqual(
			sum([ih.load_image(os.path.join(tile_dir_path, tile_name)).size[0] for tile_name in tile_names if re.compile('\d_0\.jpg$').match(tile_name)]), 875
		)
		# Check if all tiles in column x = 0 make up the same height of the original image
		self.assertEqual(
			sum([ih.load_image(os.path.join(tile_dir_path, tile_name)).size[1] for tile_name in tile_names if re.compile('0_\d\.jpg$').match(tile_name)]), 625
		)

	def test_shrink_exception(self):
		img = Photo(TEST_IMAGE_PATH)
		with self.assertRaises(ValueError):
			img.shrink(-1)

	def test_shrink(self):
		img = Photo(TEST_IMAGE_PATH)
		img.shrink(0.5)
		self.assertEqual(img.width, 438)
		self.assertEqual(img.height, 313)
