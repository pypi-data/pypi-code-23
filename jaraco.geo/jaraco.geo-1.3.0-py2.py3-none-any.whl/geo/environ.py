import os


def setup_environment():
	"""
	Add the data directory environment variable. This must be done
	before the geotrans2_lib is loaded (because that's where the
	library is loaded, and the environment is set at load time).
	"""
	data_path = os.path.join(os.path.dirname(__file__), 'data')
	assert os.path.exists(os.path.join(data_path, '7_param.dat'))
	key = 'GEOTRANS_DATA'
	os.environ[key] = data_path


setup_environment()
