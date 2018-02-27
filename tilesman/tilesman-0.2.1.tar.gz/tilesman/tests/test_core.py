import os
import unittest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tilesman.tests.helpers.image_handling as ih
import tilesman.tests.helpers.file_system as fs
from tilesman.core import photo_tiling, batch_photo_tiling


TEST_DIR_PATH = os.path.join('.', 'test_tmp')
TEST_IMAGE_NAME = 'test_image'
TEST_IMAGE_FORMAT = 'tif'
TEST_IMAGE_PATH = os.path.join(TEST_DIR_PATH, '.'.join([TEST_IMAGE_NAME, TEST_IMAGE_FORMAT]))
IMAGE_TILES_DIR_PATH = os.path.join(TEST_DIR_PATH, 'tiles', TEST_IMAGE_NAME)

class TestCore(unittest.TestCase):
	'''
	Integration tests for the tiling methods on module 'core'. Most of the tests will be triggered
	on the 'batch_photo_tiling' method, which consequently will also test method 'photo_tiling' as
	a by-product
	'''

	def setUp(self):
		fs.create_dir(TEST_DIR_PATH)

	def tearDown(self):
		fs.delete_dir(TEST_DIR_PATH)

	def __inspect_tile_dimensions(self, tile_inspection_scenarios):
		'''
		Verify if actual and expected tile dimensions match
		'''

		for level, (x, y), (width, height) in tile_inspection_scenarios:
			tile_path = os.path.join(IMAGE_TILES_DIR_PATH, str(level), '_'.join([str(x), str(y)]) + '.tif')
			self.assertEqual(ih.load_image(tile_path).size, (width, height))

	def test_raises_exception_for_non_image_file(self):
		ih.mock_image_file(TEST_IMAGE_PATH, 1, 1)
		ih.mock_generic_file(TEST_DIR_PATH, 'non_image_file.txt')

		with self.assertRaises(OSError):
			photo_tiling(os.path.join(TEST_DIR_PATH, 'non_image_file.txt'), 10, 10, ignore_input_file_exception = False)

	def test_tiling_empty_directory(self):
		batch_photo_tiling(TEST_DIR_PATH, 10, 10)

		# Checking directory structure and file count
		self.assertEqual(fs.recursive_file_count(TEST_DIR_PATH), 0)
		self.assertEqual(fs.recursive_dir_count(TEST_DIR_PATH), 0)

	def test_tiling_single_pixel_image(self):
		ih.mock_image_file(TEST_IMAGE_PATH, 1, 1)

		batch_photo_tiling(TEST_DIR_PATH, 5, 10)

		# Checking directory structure and file count
		self.assertEqual(sorted(fs.scan_dir(IMAGE_TILES_DIR_PATH)), ['0'])
		self.assertEqual(fs.recursive_file_count(os.path.join(IMAGE_TILES_DIR_PATH, '0')), 1)

		# Checking some tiles at critical positions
		# scenario = (level, (x_index, y_index), (width, height))
		tile_inspection_scenarios = [(0, (0, 0), (1, 1)),] # the only tile produced at level 0
		self.__inspect_tile_dimensions(tile_inspection_scenarios)

	def test_tiling_regular_image(self):
		ih.mock_image_file(TEST_IMAGE_PATH, 7000, 5000)

		batch_photo_tiling(TEST_DIR_PATH, 256, 256)

		# Checking directory structure and file count
		self.assertEqual(sorted(fs.scan_dir(IMAGE_TILES_DIR_PATH)), ['0', '1', '10', '11', '12', '13', '2', '3', '4', '5', '6', '7', '8', '9'])
		self.assertEqual(fs.recursive_file_count(os.path.join(IMAGE_TILES_DIR_PATH, '0')), 1)
		self.assertEqual(fs.recursive_file_count(os.path.join(IMAGE_TILES_DIR_PATH, '10')), 12)
		self.assertEqual(fs.recursive_file_count(os.path.join(IMAGE_TILES_DIR_PATH, '13')), 560)

		# Checking some tiles at critical positions
		# scenario = (level, (x_index, y_index), (width, height))
		tile_inspection_scenarios = [
			(0, (0, 0), (1, 1)), # the only tile produced at level 0
			(10, (1, 1), (256, 256)), # a full-dimensioned tile at level 10
			(10, (3, 0), (107, 256)), # a level 10 tile at the edge of x axis
			(10, (0, 2), (256, 113)), # a level 10 tile at the edge of y axis
			(10, (3, 2), (107, 113)), # the level 10 tile at the edge of x and y axes
			(13, (15, 15), (256, 256)), # a full-dimensioned tile at level 13
			(13, (27, 5), (88, 256)), # a level 13 tile at the edge of y axis
			(13, (10, 19), (256, 136)), # a level 13 tile at the edge of y axis
			(13, (27, 19), (88, 136)), # the level 13 tile at the edge of x and y axes
		]
		self.__inspect_tile_dimensions(tile_inspection_scenarios)

	def test_tiling_several_images_in_a_directory(self):
		amount_of_images = 5

		ih.mock_several_image_files(TEST_DIR_PATH, TEST_IMAGE_NAME, TEST_IMAGE_FORMAT, amount_of_images, 1000, 800)
		ih.mock_generic_file(TEST_DIR_PATH, 'non_image_file.txt')

		batch_photo_tiling(TEST_DIR_PATH, 150, 100)

		# Checking that the generic file did not influence the tiling process
		self.assertFalse(os.path.exists(os.path.join(TEST_DIR_PATH, 'tiles', 'non_image_file')))

		for i in range(amount_of_images):
			image_i_tiles_dir_path = IMAGE_TILES_DIR_PATH + '_' + str(i)

			# Checking directory structure and file count
			self.assertEqual(sorted(fs.scan_dir(image_i_tiles_dir_path)), ['0', '1', '10', '2', '3', '4', '5', '6', '7', '8', '9'])
			self.assertEqual(fs.recursive_file_count(os.path.join(image_i_tiles_dir_path, '0')), 1)
			self.assertEqual(fs.recursive_file_count(os.path.join(image_i_tiles_dir_path, '4')), 1)
			self.assertEqual(fs.recursive_file_count(os.path.join(image_i_tiles_dir_path, '8')), 4)
			self.assertEqual(fs.recursive_file_count(os.path.join(image_i_tiles_dir_path, '10')), 56)
