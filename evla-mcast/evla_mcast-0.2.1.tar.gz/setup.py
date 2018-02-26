#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

from setuptools import setup, find_packages

setup(name='evla_mcast',
      version='0.2.1',
      description='Receive and handle EVLA multicast messages',
      author='Paul Demorest',
      author_email='pdemores@nrao.edu',
      url='https://github.com/demorest/evla_mcast/',
      install_requires=['lxml', 'future'],
      packages=find_packages(exclude=('tests',)),
      package_data={'evla_mcast': ['xsd/*.xsd','xsd/vci/*.xsd','xsd/observe/*.xsd']},
      classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
     ],
     )
