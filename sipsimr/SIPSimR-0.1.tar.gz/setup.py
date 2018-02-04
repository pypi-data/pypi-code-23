#!/usr/bin/env python

# SETUP:
## python setup.py build_ext --inplace

from setuptools import setup, find_packages
from glob import glob

install_reqs = []

scripts = glob('scripts/*.R')

## install main application
desc = 'Simulate High Resolution Stable Isotope Probing Datasets (associated R scripts)'
setup(
    name = 'SIPSimR',
    version = '0.1',
    description = desc,
    long_description = desc + '\n See README for more information.',
    author = 'Nick Youngblut',
    author_email = 'nyoungb2@gmail.com',
    install_requires = install_reqs,
    license = "MIT license",
    packages = find_packages(),
    package_dir = {'SIPSimR':
                   'SIPSimR'},
    scripts = scripts,
    url = 'https://github.com/nick-youngblut/SIPSimR'
)




