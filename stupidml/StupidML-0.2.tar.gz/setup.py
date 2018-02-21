from distutils.core import setup

NAME = 'StupidML'
AUTHOR = 'Yash Jajoo'
EMAIL = 'yash.jajoo@gmail.com'
DESCRIPTION = 'A collection of python modules for for machine learning'
VERSION = '0.2'
PACKAGES = ['StupidML', 'StupidML.Models', 'StupidML.Utilities']
LICENSE = 'MIT License'
URL = 'https://github.com/yash1802/SimpleML/blob/master/SimpleML.tar.gz'

setup(
	name = NAME,
	author = AUTHOR,
	author_email = EMAIL, 
	version = VERSION,
	description = DESCRIPTION,
	packages = PACKAGES,
	license = LICENSE,
	url = URL,
	)
