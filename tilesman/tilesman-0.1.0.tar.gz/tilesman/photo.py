import os
from math import ceil
from tile import Tile
from PIL import Image

class InputFileException(Exception):
	pass

class InvalidResizingException(Exception):
	pass

class TilingException(Exception):
	pass

class Photo:
	'''
	Represents a photo to be tiled
	'''

	def __init__(self, path):
		try:
			self.binary = Image.open(path)
		except Exception as e:
			error_message = 'Error when trying to load file %s\n%s' % (path, e)
			raise InputFileException(error_message)
		else:
			self.path = path
			self.width, self.height = self.binary.size
			self.file_format = os.path.splitext(path)[1][1:]

	def extract_tiles(self, subdir_name, tile_max_width, tile_max_height):
		'''
		Extract and save all possible tiles from the current resolution of the photo. No tile
		will have dimensions (width or height) bigger than 'tile_max_width' and 'tile_max_height'. All
		extrated tiles will be saved in a subdirectory named 'subdir_name'
		'''

		y = 0

		try:
			# while tile coordinate y is less than the maximum height range 
			while (y < (self.height / tile_max_height)):
				x = 0
				# while tile coordinate x is less than the maximum width range
				while (x < (self.width / tile_max_width)):
					# Define top-left and lower-right corner coordinates of the tile
					x_start = x * tile_max_width
					y_start = y * tile_max_height
					x_end = x_start + min(tile_max_width, (self.width - (x * tile_max_width)))
					y_end = y_start + min(tile_max_height, (self.height - (y * tile_max_height)))

					tile_boundaries = (x_start, y_start, x_end, y_end)

					# Crop the tile from the original photo and register its coordinates
					tile_binary = self.binary.crop(tile_boundaries)
					tile_coordinates = (x, y)

					# Create and save the tile to the file system
					Tile(tile_binary, tile_coordinates, self.file_format).save(os.path.join(os.path.dirname(self.path), str(subdir_name)))

					x += 1
				y += 1
		except Exception as e:
			error_message = 'Error when tiling image %s\n%s' % (self.path, e)
			raise TilingException(error_message)

	def shrink(self, ratio):
		'''
		Scale photo resolution by 'ratio'
		'''

		scaled_width = ceil(self.width * ratio)
		scaled_height = ceil(self.height * ratio)

		try:
			self.binary = self.binary.resize((scaled_width, scaled_height))
		except Exception as e:
			error_message = 'Error when resizing photo %s to %s of its original size\n%s' % (self.path, ratio * 100, e)
			raise InvalidResizingException(error_message)
		else:
			self.width = scaled_width
			self.height = scaled_height
