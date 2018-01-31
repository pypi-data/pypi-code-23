#!/usr/bin/env python

import os
import sys
sys.path.append(os.getcwd())

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='scikit-graph',
    description="A collection of tools and algorithms to augment those found in Scipy's csgraph module",
    author='PMEAL Team',
    version='0.1alpha',
    author_email='jgostick@uwaterloo.ca',
    packages=['skgraph'],
    install_requires=['numpy',
                      'scipy']
)
