import os

class Tile:
	'''
	Represents a single tile of a photo
	'''

	def __init__(self, binary, coordinates, file_format):
		self.binary = binary
		self.width, self.height = self.binary.size
		self.coordinates = coordinates
		self.file_format = file_format

	def save(self, dest_directory):
		'''
		Saves a single tile to the destination directory 'dest_directory'
		'''

		tile_name = str(self.coordinates[0]) + '_' + str(self.coordinates[1]) + '.' + self.file_format
		file_path = os.path.join(dest_directory, tile_name)

		os.makedirs(dest_directory, exist_ok = True)
		
		self.binary.save(file_path, subsampling = 0, quality = 100)
