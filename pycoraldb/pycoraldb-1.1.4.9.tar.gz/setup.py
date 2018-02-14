#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# from setuptools import setup,
# from distutils.core import setup

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import version

NAME = "pycoraldb"
VERSION = version.__version__

install_requires = ['websocket-client>=0.44.0', 'dill>=0.2.7.1']

setup(
    name=NAME,
    version=VERSION,
    # packages=['pycoraldb'],
    packages=find_packages(),
    # package_dir={'': '..'},
    # package_data={'': ['*.md', '*.py']},
    install_requires=install_requires,
    # install_requires=['pandas>=2.1'],
    # metadata for upload to PyPI
    author='FanCapital',
    author_email='public@fancapital.com',
    description='Python CoralDB Client',
    long_description='Python CoralDB Client',
    license='FanCapital Public License',
    url='https://pypi.python.org/pypi/pycoraldb',
    keywords='pycoraldb coraldb')
