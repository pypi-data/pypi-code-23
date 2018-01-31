# -*- encoding: utf-8 -*-
"""
Python setup file for the open_discussions_client app.
"""
from __future__ import unicode_literals
import os
from setuptools import setup, find_packages

import open_discussions_api

# pylint: disable=invalid-name
dev_requires = [
    'flake8',
]

install_requires = open('requirements.txt').read().splitlines()


def read(filename):
    """Helper function to read bytes from file"""
    try:
        return open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError:
        return ''

setup(
    name="open-discussions-client",
    version=open_discussions_api.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='BSD-3',
    platforms=['OS Independent'],
    keywords='open-discussions, rest api',
    author='MIT Office of Digital Learning',
    author_email='mitx-devops@mit.edu',
    url="https://github.com/mitodl/open-discussions-client",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
)
