#!/usr/bin/env python
from distutils.core import setup, Extension
from os.path import abspath, dirname, join
import sys

MAJOR, MINOR = sys.version_info[:2]
BASE_DIR = dirname(abspath(__file__))

PKG_BASE = 'source'
DOCS_DIR = join(BASE_DIR, 'docs')

setup(
    name='uniprop',
    version='1.3',
    description='Unicode properties of codepoints.',
    long_description=open(join(DOCS_DIR, 'description.rst')).read(),

    # PyPI does spam protection on email addresses, no need to do it here
    author='Matthew Barnett',
    author_email='uniprop@mrabarnett.plus.com',

    maintainer='Matthew Barnett',
    maintainer_email='uniprop@mrabarnett.plus.com',

    url='https://bitbucket.org/mrabarnett/uniprop',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: General',
        ],
    license='Apache License, Version 2.0',

    package_dir={'': PKG_BASE},

    ext_modules=[Extension('uniprop', [join(PKG_BASE, 'unicode_tables.c'), join(PKG_BASE, 'uniprop.c')])],
    )
