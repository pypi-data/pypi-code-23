#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pip setup for bjoda
"""
import sys
import os
from os.path import (
    dirname
)
from bjoda.globals import (
    __version__
)
from setuptools import (
    setup
)


LOCAL_PATH = os.path.abspath(dirname(__file__))
REQUIRED_PACKAGES = [
    'pexpect>=4.1.0'
]


if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist bdist_wheel upload')
    sys.exit()


setup(
    name='bjoda',
    version=__version__,
    description='Better syscalls and commands from python',
    long_description='',
    author='Jacobi Petrucciani',
    author_email='jacobi@mimirhq.com',
    url='',
    py_modules=['bjoda'],
    install_requires=REQUIRED_PACKAGES,
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
