#! /usr/bin/python
from setuptools import setup, find_packages

import os

_HERE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

from setuptools.command.install import install as _install






with open(os.path.join(_HERE, 'README.rst'),'r+') as fh:
    long_description = fh.read()

setup(
    name = "rekog2json2mongo",
    version = "0.0.2",
    description = "call AWS rekognition api, pushing local images, saving api results to json as well as mongodb",
    long_description = long_description,
    author = "Shichao(Richard) Ji",
    author_email = "jshichao@vt.edu",
    url = "https://github.com/shichaoji/rekog2json2mongo",
    download_url = "https://github.com/shichaoji/rekog2json2mongo/archive/0.1.tar.gz",
    keywords = ['database','ETL','mongodb','rekognition'],
    license = 'MIT', 
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        ],
    packages = find_packages(),
    install_requires=[
        'pymongo',
        'boto3'
      ],
    entry_points={
        'console_scripts': ['face2mongo=rekog2json2mongo:main'],
      },
)

