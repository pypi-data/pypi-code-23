#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

requirements = [
    'grpcio',
    'protobuf'
]

setup(
    name="buffer_buda",
    version='0.5.3',
    packages=find_packages(),
    install_requires=requirements,
)
