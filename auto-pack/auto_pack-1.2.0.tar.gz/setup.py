#!/usr/bin/env python
# -*-coding:utf-8-*-

import ast
import re
try:
    from setuptools import setup
except:
    from distutils.core import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('auto_pack/__init__.py') as f:
    VERSION = ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))

NAME = "auto_pack"

PACKAGES = ["auto_pack", ]
DESCRIPTION = "qudian Android auto pack utils"
LONG_DESCRIPTION = open("README.rst").read()

KEYWORDS = ["android", "Android", "auto_pack"]

AUTHOR = "meng"
AUTHOR_EMAIL = "mengweiping@qudian.com"
LICENSE = "MIT"

URL = "http://www.qudian.com"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms="any",
    install_requires=['android-utils','progressbar-ipython'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
