#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

lib_version = os.environ.get('LIB_VERSION', '').strip().replace('v', '')
if not lib_version:
    raise ValueError('ava_engine must have a lib_version before publishing. `LIB_VERSION=0.0.1 python setup.py sdist`')

setup(
    name='ava_engine',
    version=lib_version,
    description='Official Ava Engine Python SDK.',
    author='Image Intelligence',
    author_email='support@imageintelligence.com',
    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['test*']),
    install_requires=[
        'grpcio==1.8.4',
    ],
    include_package_data=True,
    package_data={'': ['README.md', 'LICENSE.md']},
)
