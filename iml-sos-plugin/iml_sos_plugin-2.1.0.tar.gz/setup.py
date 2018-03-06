#!/usr/bin/env python

# Copyright (c) 2018 Intel Corporation. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from setuptools import setup, find_packages
from iml_sos_plugin import package_version

setup(
    name='iml_sos_plugin',
    version=package_version(),
    author="Intel Corporation",
    author_email="iml@intel.com",
    url='https://pypi.python.org/pypi/iml_sos_plugin',
    packages=find_packages(exclude=["*tests*"]),
    include_package_data=True,
    license='MIT',
    description='IML sosreport plugin',
    long_description="""
    A sosreport plugin for collecting IML data
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='IML lustre high-availability',
    entry_points={
        'console_scripts': [
            'iml-diagnostics = iml_sos_plugin.cli:main',
            'chroma-diagnostics = iml_sos_plugin.cli:chroma_diagnostics'
        ]
    })
