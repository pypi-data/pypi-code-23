#!/usr/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.
#
from distutils.core import setup
from setuptools import find_packages

import bdworkbench

setup(
    name = 'bdworkbench',
    packages = find_packages(),
    version = bdworkbench.__version__,
    description = 'Appstore SDK for BlueData EPIC platform.',

    zip_safe=False,
    include_package_data=True,

    author = 'BlueData Software, Inc.',
    author_email = 'support@bluedata.com',
    url = 'https://github.com/bluedatainc/catalogsdk',
    keywords = [ 'BlueData', 'appstore', 'catalog', 'EPIC'],

    entry_points = {
        "console_scripts" : [ 'bdwb=bdworkbench.__main__:main' ],
    },
    install_requires = [
        'argparse >= 1.2.1',
        'requests >=2.6.0'
    ],
    classifiers = [
            "Environment :: Console",
            "Natural Language :: English",
            "Programming Language :: Python",
            "Intended Audience :: Developers",
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: Implementation :: CPython",
    ]
)
