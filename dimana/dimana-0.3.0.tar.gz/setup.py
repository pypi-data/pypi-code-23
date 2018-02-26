#! /usr/bin/env python

from setuptools import setup, find_packages

PKG = 'dimana'

setup(
    name=PKG,
    description='Dimensional Analysis - arithmetic with measurement units.',
    author='Nathan Wilcox',
    author_email='nejucomo@gmail.com',
    version='0.3.0',
    url='https://github.org/nejucomo/{}'.format(PKG),
    license='TGPPLv1.0',
    install_requires=[
        'future == 0.16.0',
    ],
    package_data={PKG: ['../README.rst']},
    packages=find_packages(),
)
