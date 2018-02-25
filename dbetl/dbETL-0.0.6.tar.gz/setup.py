#! /usr/bin/python
from setuptools import setup, find_packages

import os

_HERE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

from setuptools.command.install import install as _install






with open(os.path.join(_HERE, 'README.rst'),'r+') as fh:
    long_description = fh.read()

setup(
    name = "dbETL",
    version = "0.0.6",
    description = "database batch ETL helper",
    long_description = long_description,
    author = "Shichao(Richard) Ji",
    author_email = "jshichao@vt.edu",
    url = "https://github.com/shichaoji/dbETL",
    download_url = "https://github.com/shichaoji/dbETL/archive/0.1.tar.gz",
    keywords = ['database','ETL','mysql','scrapyhub'],
    license = 'MIT', 
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        ],
    packages = find_packages(),
    install_requires=[
        'pymysql',
      ],
    entry_points={
        'console_scripts': ['dbETL=dbETL:main','dbpreset=dbETL:preset'],
      },
)

