#!/usr/bin/env python
from setuptools import setup, find_packages

requires = ['Sphinx>=0.6',
        #'ditaa>=0.9',
        ]

setup(
    name='sphinxcontrib-ditaa',
    version='0.4',
    url='https://github.com/stathissideris/ditaa',
    license='BSD',
    author='Yongping Guo',
    author_email='guoyoooping@163.com',
    description='Ditaa Sphinx extension',
    long_description=open('README.rst').read(),
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
