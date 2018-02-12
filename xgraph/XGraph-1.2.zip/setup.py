from distutils.core import setup
try:
	import pypandoc
	long_descrpt = pypandoc.convert('README.md','rst')
except(IOError,ImportError):
	long_descrpt = open('README.md').read()

setup(
	name = 'XGraph',
	version = '1.2',
	description = 'Open-source package for graphs,graph-algorithms',
	long_description  = long_descrpt,
	author = 'DigitMan27',
	author_email = 'digitman27@gmail.com',
	url = 'https://github.com/DigitMan27/XGraph',
	download_url = ['https://github.com/DigitMan27/XGraph/archive/v1.2.zip',
					'https://github.com/DigitMan27/XGraph/archive/v1.2.tar.gz'],
	packages = ['XGraph',]
	)
