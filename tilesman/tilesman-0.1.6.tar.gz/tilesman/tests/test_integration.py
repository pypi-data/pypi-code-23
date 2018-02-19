import os
import unittest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tilesman.tests.helpers.image_handling as ih
import tilesman.tests.helpers.file_system as fs
from tilesman.core import run


test_dir = os.path.join('.', 'test_tmp')
test_image_path = os.path.join(test_dir, 'test_image.tif')

class TestIntegration(unittest.TestCase):
	'''
	Integration tests for the application modules. Focus is on main module
	We are not testing every single tile created, as this would require duplicating the tiling
	algorith as a test helper
	'''

	def setUp(self):
		fs.create_dir(test_dir)

	def tearDown(self):
		fs.delete_dir(test_dir)

	def __inspect_tile_dimensions(self, tile_inspection_scenarios):
		'''
		Verify if actual and expected tile dimensions match
		'''

		for level, (x, y), (width, height) in tile_inspection_scenarios:
			self.assertEqual(ih.load_image(os.path.join(test_dir, str(level), '_'.join([str(x), str(y)]) + '.tif')).size, (width, height))

	def test_tiling_large_image(self):
		ih.mock_image_on_file_system(test_image_path, 7000, 5000)

		run(test_image_path, 256, 256)

		# Checking directory structure and file count
		self.assertEqual(fs.recursive_dir_count(test_dir), 14)
		self.assertEqual(sorted(fs.scan_dir(test_dir)), ['0', '1', '10', '11', '12', '13', '2', '3', '4', '5', '6', '7', '8', '9'])
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '0')), 1)
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '10')), 12)
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '13')), 560)

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

	def test_tiling_medium_image(self):
		ih.mock_image_on_file_system(test_image_path, 1000, 800)

		run(test_image_path, 34, 67)

		# Checking directory structure and file count
		self.assertEqual(fs.recursive_dir_count(test_dir), 11)
		self.assertEqual(sorted(fs.scan_dir(test_dir)), ['0', '1', '10', '2', '3', '4', '5', '6', '7', '8', '9'])
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '0')), 1)
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '6')), 2)
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '10')), 360)

		# Checking some tiles at critical positions
		# scenario = (level, (x_index, y_index), (width, height))
		tile_inspection_scenarios = [
			(0, (0, 0), (1, 1)), # the only tile produced at level 0
			(6, (0, 0), (34, 50)), # a level 6 tile at the edge of y axis
			(6, (1, 0), (29, 50)), # the level 6 tile at the edge of x and y axes
			(10, (9, 10), (34, 67)), # a full-dimensioned tile at level 10
			(10, (29, 7), (14, 67)), # a level 10 tile at the edge of y axis
			(10, (3, 11), (34, 63)), # a level 10 tile at the edge of y axis
			(10, (29, 11), (14, 63)), # the level 10 tile at the edge of x and y axes
		]
		self.__inspect_tile_dimensions(tile_inspection_scenarios)

	def test_tiling_small_image(self):
		ih.mock_image_on_file_system(test_image_path, 20, 20)

		run(test_image_path, 15, 15)

		# Checking directory structure and file count
		self.assertEqual(fs.recursive_dir_count(test_dir), 6)
		self.assertEqual(sorted(fs.scan_dir(test_dir)), ['0', '1', '2', '3', '4', '5'])
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '0')), 1)
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '2')), 1)
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '5')), 4)

		# Checking some tiles at critical positions
		# scenario = (level, (x_index, y_index), (width, height))
		tile_inspection_scenarios = [
			(0, (0, 0), (1, 1)), # the only tile produced at level 0
			(2, (0, 0), (3, 3)), # the only tile produced at level 2
			(5, (0, 0), (15, 15)), # a full-dimensioned tile at level 5
			(5, (1, 0), (5, 15)), # a level 5 tile at the edge of y axis
			(5, (0, 1), (15, 5)), # a level 5 tile at the edge of y axis
			(5, (1, 1), (5, 5)), # the level 5 tile at the edge of x and y axes
		]
		self.__inspect_tile_dimensions(tile_inspection_scenarios)

	def test_tiling_single_pixel_image(self):
		ih.mock_image_on_file_system(test_image_path, 1, 1)

		run(test_image_path, 5, 10)

		# Checking directory structure and file count
		self.assertEqual(fs.recursive_dir_count(test_dir), 1)
		self.assertEqual(sorted(fs.scan_dir(test_dir)), ['0'])
		self.assertEqual(fs.recursive_file_count(os.path.join(test_dir, '0')), 1)

		# Checking some tiles at critical positions
		# scenario = (level, (x_index, y_index), (width, height))
		tile_inspection_scenarios = [(0, (0, 0), (1, 1)),] # the only tile produced at level 0
		self.__inspect_tile_dimensions(tile_inspection_scenarios)
