#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from setuptools import setup, find_packages


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        return fp.read()


def readlines(fname):
    return [l.strip() for l in read(fname).strip().splitlines()]


install_requires = [
    'MarkupSafe>=1.0',
    'strict-rfc3339>=0.7'
]
tests_require = [
    'PyYAML>=3.12',
    'colorama>=0.3.7',
    'pytest>=3.0.3'
]

long_description = read('README.rst')


setup(
    name='Inukshuk',
    use_scm_version={'write_to': 'inukshuk/version.py'},
    description='A template engine.',
    long_description=long_description,
    author='Ludovic Chabant',
    author_email='ludovic@chabant.com',
    license="Apache License 2.0",
    url='https://bolt80.com/inukshuk',
    keywords='template engine',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['setuptools_scm', 'pytest-runner'],
    tests_require=tests_require,
    install_requires=install_requires,
)
