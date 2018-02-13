#!/usr/bin/env python
from setuptools import setup, find_packages
import sys
from os import path

if sys.version_info < (3, 6):
    raise RuntimeError("Python < 3.6 is not supported!")

#here = path.abspath(path.dirname(__file__))
#with open(path.join(here, 'README.rst')) as file:
#    long_description = file.read()

setup(
    name='nots',
    version='0.0.1',
    description="Not obviously traditional serialization.",
#    long_description=long_description,
#    url='https://github.com/prokopst/nots',
    packages=find_packages(exclude=['tests']),
    author="Stan Prokop",
    license='Apache License, version 2.0',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="serialization deserialization json",
    test_suite='tests',
)
