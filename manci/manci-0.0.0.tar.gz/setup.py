#!/usr/bin/env python
# Licensed under a 3-clause BSD style license, see LICENSE.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

from setuptools import find_packages
from setuptools import setup


def get_version():
    g = {}
    exec(open(os.path.join('manci', 'version.py')).read(), g)
    return g['__version__']


setup(name='manci',
      version=get_version(),
      packages=find_packages(exclude=['tests']),
      scripts=[],
      data_files=[],
      description='Convert between different style of formulae',
      long_description=None,
      author='Chris Burr',
      author_email='c.b@cern.ch',
      maintainer='Chris Burr',
      maintainer_email='c.b@cern.ch',
      url='https://github.com/chrisburr/manci',
      download_url='https://github.com/chrisburr/manci/releases',
      license='BSD 3-clause',
      test_suite='tests',
      install_requires=['numpy', 'pyparsing', 'colorlog', 'aenum'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Utilities',
          ],
      platforms='Any',
      )
