#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

import pypandoc
from setuptools import find_packages, setup

# package variables
package = 'tapioca_cloudez'
readme = pypandoc.convert('README.md', 'rst')
requirements = [
    'tapioca-wrapper<2',
]
test_requirements = [
]

# dynamic package info
init_py = open(os.path.join(package, '__init__.py')).read()
version = re.search(
    "^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)
author = re.search(
    "^__author__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)
email = re.search(
        "^__email__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)

setup(
    name='tapioca-cloudez',
    version=version,
    description='cloudez API wrapper using tapioca',
    long_description=readme,
    author=author,
    author_email=email,
    url='https://github.com/humrochagf/tapioca-cloudez',
    packages=find_packages(),
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='cloudez',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
