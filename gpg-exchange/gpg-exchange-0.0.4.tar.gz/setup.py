#!/usr/bin/env python

"""
Package setup script for GPG exchange.

Copyright 2018 Leon Helwerda

GPP exchange is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

GPG exchange is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <https://www.gnu.org/licenses/>.
"""

try:
    from builtins import str
except ImportError:
    pass
from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup, find_packages
from gpg_exchange import __version__

setup(name='gpg-exchange',
      version=__version__,
      description='Simplified GPG exchange',
      long_description='''Simplified GPG exchange wrapper.
This module abstracts some of the data types and operations performed by the
GPG Made Easy library in order to provide a single means of key generation,
public key exchange, encryption and decryption using GPG.''',
      author='Leon Helwerda',
      author_email='l.s.helwerda@liacs.leidenuniv.nl',
      url='https://github.com/lhelwerd/gpg-exchange',
      license='GPL3+',
      packages=find_packages(),
      entry_points={},
      include_package_data=True,
      install_requires=[
          str(requirement.req)
          for requirement in parse_requirements('requirements.txt',
                                                session=PipSession())
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Topic :: Security :: Cryptography'],
      keywords=['gpg', 'exchange'])
