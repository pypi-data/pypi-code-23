#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# System modules
import os
import glob
from setuptools import setup, find_packages

__version__ = "0.0.10"

def read_file(filename):
    with open(filename) as f:
        return f.read()

# run setup
# take metadata from setup.cfg
setup( 
    name = "meteorology",
    description = "utilities for meteorological calculations",
    long_description = read_file("README.rst"),
    author = "Yann Büchau",
    author_email = "yann.buechau@web.de",
    keywords = "meteorology",
    version = __version__,
    license = 'GPLv3',
    url = 'https://gitlab.com/nobodyinperson/python3-meteorology',
    classifiers = [
	'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
	'Programming Language :: Python :: 3.5',
	'Operating System :: OS Independent',
	'Topic :: Scientific/Engineering :: Atmospheric Science',
        ],
    test_suite = 'tests',
    tests_require = [ 'numpy' ],
    install_requires = [ 'numpy' ],
    packages = find_packages(exclude=['tests']),
    )

