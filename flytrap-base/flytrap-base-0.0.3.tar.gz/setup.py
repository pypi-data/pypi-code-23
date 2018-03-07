#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="flytrap-base",
    version="0.0.3",
    author="flytrap",
    author_email="hiddenstat@gmail.com",
    description="A simple Django app to base",
    long_description=README,
    url="https://github.com/flytrap/flytrap-base",
    install_requires=[
        "Django>=2.0",
        "djangorestframework>=3.7.3",
        "django-filter>=1.1.0",
        "django-rest-framework-mongoengine>=3.3.1"
    ],
    packages=find_packages(),
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
