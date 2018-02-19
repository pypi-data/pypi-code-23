# /usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>

"""

from setuptools import setup, find_packages

setup(
    name='cdumay-rest-client',
    version=open('VERSION', 'r').read().strip(),
    description="HTTP client",
    long_description=open('README.rst', 'r').read().strip(),
    classifiers=["Programming Language :: Python"],
    keywords='',
    author='Cedric DUMAY',
    author_email='cedric.dumay@gmail.com',
    url='https://github.com/cdumay/cdumay-rest-client',
    license='Apache License',
    include_package_data=True,
    zip_safe=True,
    install_requires=open('requirements.txt', 'r').readlines(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    test_suite="cdumay_rest_client.tests",
)
