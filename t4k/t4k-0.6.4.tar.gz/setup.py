#!/usr/bin/env python
from setuptools import setup

setup(
	name='t4k',
	url='http://drgitlab.cs.mcgill.ca/enewe101/trix_for_kids',
	version='0.6.4',
	description='my personal swiss army knife',
	author='edward newell',
	author_email='edward.newell@gmail.com',
	packages=['t4k'],
	license='MIT',
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Information Technology',
		'Programming Language :: Python :: 2.7',
		'Natural Language :: English',
		'Topic :: Utilities',
	],
	keywords='trix are for kids',
	install_requires=[
        'numpy', 'psutil', 'natsort', 'Pyro4', 'setproctitle', 'tastypy'
    ],
    scripts=['bin/mem-server']
)

