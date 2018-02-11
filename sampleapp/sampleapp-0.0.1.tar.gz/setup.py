#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = '0.0.1'

setup(name='sampleapp',
    version=VERSION,
    description="a sample project",
    long_description=long_description, # Optional
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='python package demo sample',
    author='hyteer@gmail.com',
    author_email='hyteer@gmail.com',
    url='https://github.com/hyteer/pypi-sample',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
    entry_points={
        'console_scripts': [ 'aptool = sampleapp:main' ]
    },
)
