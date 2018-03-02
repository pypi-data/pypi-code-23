#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path
# -------------------------------------------------------------------
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# -------------------------------------------------------------------
setup(name='sat5ptools',
	description='5P Self Assessment Tools - commands to work with sat5p conversations',
	author='Daniel Baird',
	author_email='daniel@danielbaird.com',
	url='https://github.com/DanielBaird/self-assessment-tool',
	long_description=long_description,
	license='Apache2',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'License :: OSI Approved :: Apache Software License'
	],
	keywords='chat 5p selfassessment conversation',
	version='0.2.2',
	py_modules=['sat5ptools'],
	install_requires=[
		'Click',
		'openpyxl'
	],
	entry_points='''
		[console_scripts]
		excel2qns=sat5ptools:excel2qns
		excel2graph=sat5ptools:excel2graph
		excel2all=sat5ptools:excel2all
		sat5pconfig=sat5ptools:sat5pconfig
	'''
)
