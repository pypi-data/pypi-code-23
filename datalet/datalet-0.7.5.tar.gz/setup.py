#!/usr/bin/env python
# -*- coding: utf-8  -*-

from setuptools import setup, find_packages

from datalet import __version__

setup(
	name = 'datalet',
	version = __version__,
	packages = find_packages(),
	keywords = ['datalet'],
	author = 'li pei',
	author_email = 'pei@ilanever.com',
	description = 'datalet is a toolkit for data analysis.',
	long_description = open('README.rst').read(),
	include_package_data = True,
	url = 'https://github.com/lipei86/datalet',
	install_requires=[
		'openpyxl>=2.5.0a3',
		'xlrd>=1.1.0',
		'xlwt>=1.3.0',
		'python-dateutil>=2.6.1',
		'cchardet>=2.1.1'
	]
	)
