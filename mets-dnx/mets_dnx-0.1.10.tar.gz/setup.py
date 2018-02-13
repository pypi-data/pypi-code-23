try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION='0.1.10'

config = {
	'name':'mets_dnx',
	'version':VERSION,
	'author':'Sean Mosely',
	'author_email':'sean.mosely@gmail.com',
	'packages':['mets_dnx',],
	'description':'Python library for building Rosetta DNX/METS XML documents',
	'install_requires':['lxml>=3.6.4', 'pymets','pydc', 'pydnx'],
	'download_url': 'https://github.com/NLNZDigitalPreservation/mets_dnx/archive/v'+VERSION+'.tar.gz',
	'license': 'MIT',
	}

setup(**config)