#!/usr/bin/env python
# -*- coding: utf-8 -*

from __future__ import absolute_import

import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='aioimdb',
    version='1.0',
    packages=['aioimdb', ],
    include_package_data=True,
    zip_safe=False,
    description=(
        'Python asyncio IMDB client using the IMDB json web service made '
        'available for their iOS app.'
    ),
    author='Francesco Pierfederici',
    author_email='fpierfed@megabeets.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='https://github.com/fpierfed/aioimdb',
    url='https://github.com/fpierfed/aioimdb',
    download_url='https://github.com/fpierfed/aioimdb/archive/1.0.tar.gz',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: AsyncIO',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
