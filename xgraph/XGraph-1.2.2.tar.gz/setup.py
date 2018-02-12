from distutils.core import setup

setup(
	name = 'XGraph',
	version = '1.2.2',
	description = 'Open-source package for graphs,graph-algorithms',
	long_description  = open('README.rst').read(),
	author = 'DigitMan27',
	author_email = 'digitman27@gmail.com',
	url = 'https://github.com/DigitMan27/XGraph',
	download_url = ['https://github.com/DigitMan27/XGraph/archive/v1.2.2.zip',
					'https://github.com/DigitMan27/XGraph/archive/v1.2.2.tar.gz'],
	packages = ['XGraph',]
	)
