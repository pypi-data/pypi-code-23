#!/usr/bin/env python

import os
import shutil
import platform
import sys
import warnings
import json
from glob import glob

try:
    # Use setuptools if available, for install_requires (among other things).
    import setuptools
    from setuptools import setup, Extension
except ImportError:
    setuptools = None
    from distutils.core import setup, Extension

# Classic setup.py

kwargs = {}

# Version configuration
with open('rook/rookout-config.json', 'r') as f:
    config = json.load(f)
version = config['VersionConfiguration']['VERSION']


# Readme
with open('README.rst') as f:
    kwargs['long_description'] = f.read()

# Extension modules
try:
    USE_CYTHON = os.environ['USE_CYTHON']
except:
    USE_CYTHON = 'sdist' in sys.argv or 'test' in sys.argv

if 'CPython' == platform.python_implementation():
    ext_modules = []

    if 'Linux' in platform.system() and platform.python_version().startswith('2.7'):
        ext_modules.append(Extension(
            'rook.services.cdbg_native',
            sources=glob('rook/services/native/*.cc'),
            extra_compile_args=[
                '-std=c++0x',
                '-Werror',
                '-g0',
                '-O3',
            ],
            libraries=['rt']))

    ext = '.pyx' if USE_CYTHON else '.c'
    cython_extensions = [Extension("rook.services.pyx_bdb", ["rook/services/pyx_bdb"+ext])]
    if USE_CYTHON:
        from Cython.Build import cythonize
        cython_extensions = cythonize(cython_extensions)
    ext_modules += cython_extensions

    kwargs['ext_modules'] = ext_modules

if setuptools is not None:
    # If setuptools is not available, you're on your own for dependencies.
    install_requires = [
        "six>=1.9",
        "grpcio==1.4.0",
    ]

    kwargs['install_requires'] = install_requires

setup(
    name="rook",
    version=version,
    packages=setuptools.find_packages(where='.', exclude=['contrib', 'docs', '*test*']),
    include_package_data=True,
    author="Rookout",
    author_email="liran@rookout.com",
    url="http://rookout.com/",
    description="Rook is a Python package for on the fly debugging and data extraction for application in production",
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',

        ],
    zip_safe=False,
    test_suite='tests',
    **kwargs
)
