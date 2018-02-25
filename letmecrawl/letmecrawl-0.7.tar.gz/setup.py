#!/usr/bin/env python

import os
import sys

from setuptools import setup

name = "letmecrawl"

rootdir = os.path.abspath(os.path.dirname(__file__))

# Restructured text project description read from file
long_description = open(os.path.join(rootdir, 'README.rst')).read()

# Python 2.7 or later needed
if sys.version_info < (2, 7, 0, 'final', 0):
    raise SystemExit, 'Python 2.7 or later is required!'

# Data files used e.g. in tests
# package_data = {name: 'letmecrawl/sources.json'}

# Build a list of all project modules
packages = []
for dirname, _, filenames in os.walk(name):
        if '__init__.py' in filenames:
            packages.append(dirname.replace('/', '.'))

package_dir = {name: name}

setup(
    name=name,
    version='0.7',
    description='let me crawl',
    long_description=long_description,
    url='https://github.com/montenegrodr/letmecrawl',
    author='Robson Montenegro',
    author_email='montenegrodr@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    download_url='https://github.com/montenegrodr/letmecrawl/archive/0.0.5.tar.gz',
    keywords='scrape crawl',
    packages=packages,
    package_dir=package_dir,
    # package_data=package_data,
    install_requires=['six'],
    include_package_data=True
)
