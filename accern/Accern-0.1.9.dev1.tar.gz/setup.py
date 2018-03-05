#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'accern'))
from version import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info <= (2, 7):
    error = 'Requires Python Version 2.7 or above... exiting.'
    print (sys.stderr, error)
    sys.exit(1)

__long_description__ = """
*Accern*: A Python library for Accern's API.

Accern primarily serves institutional investors. The majority of our current
clients are quantitative hedge funds. Many small firms are coming to us
because of our flexible and affordable pricing options. Large firms are coming
to us due to our dedicated support, news source customization, and much more.
Aside from hedge funds, our existing clients include pension and endowment
funds, banks, brokerage firms, and more.

Accern library for Python helps user to get fast, flexible data structures from
Accern historical and streaming api.

All Accern wheels from PyPI are MIT licensed.

"""

__requirements__ = [
    'requests>=2.18.4',
    'six>=1.10.0'
]

setup(
    name='Accern',
    version=__version__,
    description="A python library for Accern Data API",
    long_description=__long_description__,
    license='MIT License',
    url="https://github.com/Accern/accern-python",
    packages=['accern'],
    package_data={"accern": ['data/*.json']},
    platforms='Posix; MacOS X; Windows',
    setup_requires=__requirements__,
    include_package_data=True,
    install_requires=__requirements__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
