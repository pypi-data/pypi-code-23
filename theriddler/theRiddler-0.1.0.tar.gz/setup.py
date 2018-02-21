from codecs import open
from os import path

try:
	from setuptools import setup

except ImportError:
	from distutils.core import setup
	
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
	description='Sample project for the lecture "Introduction to Python" of the HTWG Konstanz.',
	long_description=long_description,
	author='Etienne Martin',
	author_email='etienne.martin@htwg-konstanz.de',
	name='theRiddler',
	license='MIT',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3.6',
		'Intended Audience :: Education',
		'Natural Language :: English',
	],
	keywords='theriddler theRiddler RIDDLER Riddler riddler riddles sample learning quiz',
	packages=['theriddler'],
	include_package_data=True,
	#url='pass',
	#download_url='pass',
	version='0.1.0',
	install_requires=['nose', 'Pillow', 'beautifulsoup4', 'urllib3', 'certifi'],
	test_suite='nose.collector'
)