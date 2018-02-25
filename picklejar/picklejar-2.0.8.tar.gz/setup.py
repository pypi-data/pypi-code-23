#!/usr/bin/env python2
# coding=utf-8
"""Setup script for picklejar Python module"""

from setuptools import setup

setup(name='picklejar',
      version='2.0.8',
      description='Read and write pickles to a single file',
      author='Jesse Almanrode',
      author_email='jesse@almanrode.com',
      url='http://picklejar.readthedocs.io/',
      py_modules=['picklejar'],
      license='GNU Lesser General Public License v3 or later (LGPLv3+)',
      install_requires=['dill==0.2.7.1',
                        ],
      platforms='any',
      classifiers=[
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      )
