#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version = '0.0.2'

setup(
    name='pymongal',
    version=__version,
    description='MongoDB Abstraction Library',
    author='Tom Klaver',
    author_email='t.klaver@esciencecenter.nl',
    license='Apache 2.0',
    url='https://github.com/research-software-directory/pymongal',
    download_url='https://github.com/Tommos0/pyzenodo/archive/%s.tar.gz' % __version,
    include_package_data=True,
    keywords=['mongodb', 'abstraction', 'orm'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
    ],
    packages=find_packages(),
    install_requires=['pymongo==3.5.0'],
    setup_requires=['pytest', 'pytest-runner'],
    tests_require=['pytest', 'pytest-runner'],
    long_description="""
A MongoDB Abstraction Library
"""
)
