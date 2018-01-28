#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
"""Collection of reusable WSGI applications

Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
All rights reserved. 
"""

import sys, os, posixpath
from setuptools import setup, find_packages

PACKAGE_NAME = 'django-hotsauce-extras'
AUTHOR = 'Etienne Robillard'
AUTHOR_EMAIL = u'tkadm30@yandex.com'
VERSION = '0.9.0'
SUMMARY = 'A collection of reusable WSGI applications'
# DESCRIPTION =  __doc__
HOMEPAGE_URL = 'https://www.isotopesoftware.ca/'
KEYWORDS = 'django-hotsauce'
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
LICENSE = 'Apache2'

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=SUMMARY, 
    #long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    keywords=KEYWORDS, 
    url=HOMEPAGE_URL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,

    # Include stuff which belong in SVN or mentioned in MANIFEST.in
    # include_package_data=True,

    # Location where packages lives
    package_dir={
        '': '.',
        'argparse2': '.'},
    packages=find_packages(),

    #classifiers=[('%s' % item) for item in safe_resource_string('notmm',
    #    'static/classifiers.txt').split('\n') if item is not ""],
    # Extend setuptools with our own command set.
    #entry_points=_commands,
    
    # Packages required when doing `setup.py install`.
    #install_requires=['MoinMoin==1.8.9'],
    zip_safe=False
)

