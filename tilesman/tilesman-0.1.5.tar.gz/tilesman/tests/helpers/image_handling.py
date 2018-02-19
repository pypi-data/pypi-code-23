from io import BytesIO
from PIL import Image

def mock_image_on_memory(width, height, image_type = 'RGB', color = (100, 100, 100)):
	'''
	Creates a dummy image. It is not saved to the file system
	'''

	return Image.new(image_type, size = (width, height), color = color)

def mock_image_on_file_system(file_name, width, height, image_type = 'RGB', color = (100, 100, 100)):
	'''
	Creates a dummy image and saves it to the file system. File type is defined as per the extension
	provided in 'file_name'
	'''

	image = mock_image_on_memory(width, height, image_type = 'RGB', color = (100, 100, 100))
	image.save(file_name)

	file = BytesIO()
	file.name = file_name
	file.seek(0)
	return file

def load_image(path):
	'''
	Loads on memory an image referenced by path
	'''
	
	return Image.open(path)

