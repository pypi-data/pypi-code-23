#!/usr/bin/env python3
# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016 Dominik George <nik@naturalnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Alternatively, you are free to use OSMAlchemy under Simplified BSD, The
# MirOS Licence, GPL-2+, LGPL-2.1+, AGPL-3+ or the same terms as Python
# itself.

import importlib.util
import os
from setuptools import setup

# Get some information for the setup
MYDIR = os.path.dirname(__file__)

# Find the version string from the __init__ file
def find_version(package_name):
    filename = os.path.join(MYDIR, package_name, "__init__.py")
    with open(filename, "r") as file:
        for line in file.readlines():
            if line.startswith("__version__"):
                version = line.split('"')[1]
                return version

setup(
    # Basic information
    name = 'OSMAlchemy',
    version = find_version("osmalchemy"),
    keywords = ['osm', 'openstreetmap', 'proxy', 'caching', 'orm'],
    description = 'OpenStreetMap to SQLAlchemy bridge',
    long_description = open(os.path.join(MYDIR, "README.rst"), "r", encoding="utf-8").read(),
    url = 'https://edugit.org/Veripeditus/OSMAlchemy',

    # Author information
    author = 'Dominik George, Eike Tim Jesinghaus',
    author_email = 'osmalchemy@veripeditus.org',

    # Included code
    packages = ["osmalchemy", "osmalchemy.util"],

    # Distribution information
    zip_safe = True,
    install_requires = [
                        'SQLAlchemy>=1.0.0',
                        'python-dateutil',
                        'overpass'
                       ],
    tests_require = [
                     'SQLAlchemy>=1.0.0',
                     'python-dateutil',
                     'overpass',
                     'psycopg2',
                     'Flask>=0.10',
                     'Flask-SQLAlchemy',
                     'testing.postgresql',
                     'testing.mysqld'
                    ],
    extras_require = {
                      'Flask': [
                                'Flask>=0.10',
                                'Flask-SQLAlchemy'
                               ]
                     },
    test_suite = 'test',
    classifiers = [
                   'Development Status :: 3 - Alpha',
                   'Environment :: Plugins',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Database',
                   'Topic :: Scientific/Engineering :: GIS',
                   'Topic :: Software Development :: Libraries :: Python Modules'
                  ]
)
