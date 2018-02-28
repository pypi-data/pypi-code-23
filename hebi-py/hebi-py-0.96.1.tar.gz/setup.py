# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See http://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
from os import path
from codecs import open
from setuptools import setup, Extension

description = """
HEBI Core python API
====================

HEBI python provides bindings for the HEBI Core library.

Documentation available at http://docs.hebi.us

"""

setup(name             = 'hebi-py',
      version          = '0.96.1',
      description      = 'HEBI Core python bindings',
      long_description = description,
      author           = 'Daniel Wright',
      author_email     = 'support@hebirobotics.com',
      url              = 'https://docs.hebi.us',
      packages         = ['hebi'],
      package_data     ={'hebi': [
        'lib/**/libhebi.so.1.0',
        'lib/**/libhebi.1.0.dylib',
        'lib/**/hebi.dll',
        '_internal/*'
      ]},
      install_requires = [
        'numpy',
        'matplotlib'
      ],
      classifiers      = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: Implementation :: CPython",
      ],
      )
