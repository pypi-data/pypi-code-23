#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
	name="yakt",
	version="v0.1-DEV",
	description="Yet another keysigning tool",
	long_description="""yakt is another keysigning tool, and is written in python 3 """,
	author="Federico Campoli",
	author_email="the4thdoctor.gallifrey@gmail.com",
	platforms=[
		"linux"
	],
	classifiers=[
		"License :: OSI Approved :: BSD License",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"Intended Audience :: Information Technology",
		"Intended Audience :: System Administrators",
		"Natural Language :: English",
		"Operating System :: POSIX :: BSD",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Topic :: Database :: Database Engines/Servers",
		"Topic :: Other/Nonlisted Topic"
	],
	python_requires='>=3.3',
	nstall_requires=[
		'argparse>=1.2.1', 
		'PyYAML>=3.12', 
		'tabulate>=0.8.1', 
	],
)
