import os
from PIL import Image

def mock_generic_file(root_dir, name):
	'''
	Creates a generic mock file
	'''

	open(os.path.join(root_dir, name), "w").close()

def mock_image_on_memory(width, height, image_type = 'RGB', color = (100, 100, 100)):
	'''
	Creates a mock image. It is not saved to the file system
	'''

	return Image.new(image_type, size = (width, height), color = color)

def mock_image_file(file_path, width, height):
	'''
	Creates a mock image and saves it to the file system. File type is defined as per the extension
	provided in 'file_path'
	'''

	image = mock_image_on_memory(width, height)
	image.save(file_path)

def mock_several_image_files(root_dir, base_name, file_format, amount, width, height):
	'''
	Creates 'amount' mock images on 'root_dir', using 'base_name' as file name prefix. All images will have
	same dimensions ('width' x 'height' pixels), be of the same 'image_type' and 'color'
	'''

	for i in range(amount):
		file_path = os.path.join(root_dir, base_name + '_' + str(i) + '.' + file_format)
		mock_image_file(file_path, width, height)

def load_image(path):
	'''
	Loads on memory an image referenced by path
	'''
	
	return Image.open(path)

