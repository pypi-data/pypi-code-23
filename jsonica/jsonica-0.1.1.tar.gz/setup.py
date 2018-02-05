#!/usr/bin/env python3
# coding:utf-8

from setuptools import setup, find_packages
# for PyPI
setup(name='jsonica',
      version='0.1.1',
      description='manage huge json as xlsx statistically.',
      author='setminami',
      author_email='set.minami@gmail.com',
      url='https://setminami.github.io/Jsonica/',
      packages=find_packages(exclude=['contrib', 'docs', 'output', 'Samples', 'tests']),
      install_requires=['openpyxl>=2.4.9', 'PyYAML>=3.12', 'jsonschema>=2.6.0'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        # f-string use
        'Programming Language :: Python :: 3.6',
      ],
    )
