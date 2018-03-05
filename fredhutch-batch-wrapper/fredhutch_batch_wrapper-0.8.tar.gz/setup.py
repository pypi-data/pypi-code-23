#!/usr/bin/env python

"setup script"

from setuptools import setup, find_packages


setup(
    name="fredhutch_batch_wrapper",
    version="0.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['boto3', 'requests'],
    author='Dan Tenenbaum',
    author_email='dtenenba@fredhutch.org',
    description='Fred Hutch Wrapper for AWS Batch',
    license='MIT',
    url='https://github.com/FredHutch/fredhutch_batch_wrapper',
)
