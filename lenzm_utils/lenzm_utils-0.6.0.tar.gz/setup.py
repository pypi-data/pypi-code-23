#!/usr/bin/env python
from __future__ import unicode_literals
from codecs import open
import os
from setuptools import setup, find_packages

# Get the long description from the relevant file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = f.read()


setup(
	name='lenzm_utils',
	version='0.6.0',
	description='Various utils including Flask projects',
	long_description=long_description,
	author='Michael Lenzen',
	author_email='m.lenzen@gmail.com',
	license='MIT',
	url='https://github.com/mlenzen/lenzm_utils',
	packages=find_packages(exclude=('tests*', 'docs', 'examples')),
	include_package_data=True,
	zip_safe=False,
	package_data={
		'': ['README.rst', 'LICENSE'],
		},
	install_requires=[
		'setuptools',
		'Flask>=0.11',
		'SQLAlchemy',
		'Flask-SQLAlchemy',
		'alembic',
		'click',
		'collections_extended',
		'openpyxl',
		'pytz',
		],
	tests_require=[
		'pytest',
		],
	# See: http://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Topic :: Software Development',
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		],
	)
