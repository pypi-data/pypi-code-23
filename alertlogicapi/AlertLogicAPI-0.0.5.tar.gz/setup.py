#!/usr/bin/env python3

# Copyright 2018 Frederick Reimer.
#
# This file is part of the AlertLogicAPI Python Package.
#
# AlertLogicAPI  Python Package is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# AlertLogicAPI  Python Package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# AlertLogicAPI Python Package.  If not, see <http://www.gnu.org/licenses/>.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



setup(name = 'AlertLogicAPI',
    version = '0.0.5',
    description = 'Alert Logic API',
    long_description='Python interface to Alert Logic API.',
    author = 'Frederick Reimer',
    author_email = 'freimer@freimer.org',
    install_requires = ['requests>=1.1.0'],
    setup_requires = ['requests>=1.1.0'],
    url = 'https://github.com/freimer/AlertLogicAPI',
    packages = ['AlertLogicAPI'],
    license = 'GPL v3',
    test_suite = 'Tests',
    platforms = 'Posix; MacOS X; Windows',
    classifiers = [ 'Development Status :: 3 - Alpha',
                    'Intended Audience :: Developers',
                    'Intended Audience :: System Administrators',
                    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                    'Operating System :: OS Independent',
                    'Topic :: System :: Networking :: Monitoring',
                    ]
)