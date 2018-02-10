##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: setup.py 4744 2018-02-10 17:07:12Z roger.ineichen $
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.kibana',
    version = '0.9.0',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Kibana logging client and server for logging without logstash",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "Zope3 z3c p01 elasticsearch logstash kibana udp",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
        ],
    url = 'http://pypi.python.org/pypi/p01.kibana',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require=dict(
        test=[
            'elasticsearch',
            'gevent',
            'greenlet',
            'p01.checker',
            'p01.geo',
            ],
        forwarder=[
            'elasticsearch',
            'gevent',
            'greenlet',
            ],
        geo=[
            'p01.geo',
            ],
        ),
    install_requires = [
        'setuptools',
        ],
    entry_points = {
        'console_scripts': [
             'forwarder = p01.kibana.scripts:main',
        ],
    },
    zip_safe = False,
    )
