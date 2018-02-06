#!/usr/bin/env python
#coding:utf8

from setuptools import setup, find_packages


setup(
		name='bbk.smartImage',
		version='1.5',
		author='babiking',
		author_email='brojackfeely@163.com',
		description='Smart Image Processing Tools...',
                long_description=open('README.md').read(),
		license='LICENSE',
   		url='https://github.com/babiking/PyPi_Tools/smartImage',
		install_requires=[
			'numpy>=1.13.3'
		],
		packages=['smartImage'],
		classifiers=[
			'Programming Language :: Python :: 2.7',
			'Programming Language :: Python :: 3.6',
			'Topic :: Scientific/Engineering :: Image Recognition',
		]
		
		
	)
