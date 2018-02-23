#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, './VERSION.txt'), 'rU') as fd:
    lib_version = fd.read().strip().replace('v', '')

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
