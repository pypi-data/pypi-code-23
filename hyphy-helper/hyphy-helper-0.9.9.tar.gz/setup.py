#!/usr/bin/env python3

from __future__ import division, print_function

import sys

from os.path import abspath, join, split
from setuptools import setup

sys.path.insert(0, join(split(abspath(__file__))[0], 'lib'))

setup(name='hyphy-helper',
      version='0.9.9',
      description='An intuitive HyPhy interface for Python',
      author='N Lance Hepler',
      author_email='nlhepler@gmail.com',
      url='http://github.com/veg/hppy',
      license='GNU GPL version 3',
      packages=['hppy'],
      package_dir={'': 'lib'},
      install_requires=[
          'hyphy-python >=0.1.8',
          'Cython >=0.22.1',
          'fakemp >= 0.9.1'
      ]
     )
