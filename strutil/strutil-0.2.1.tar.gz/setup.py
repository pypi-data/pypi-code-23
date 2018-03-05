#!/usr/bin/env python
import os, sys
from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit(0)

with open('README.rst', 'r') as f:
    long_description = f.read()

# Dynamically calculate the version based on swingtime.VERSION.
version = __import__('strutil').__version__

setup(
    name='strutil',
    url='https://github.com/dakrauth/strutil',
    author='David A Krauth',
    author_email='dakrauth@gmail.com',
    description='Simple tools for downloading, cleaning, extracting and parsing content',
    version=version,
    long_description=long_description,
    platforms=['any'],
    license='MIT License',
    py_modules=['strutil'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing'
    ),
)
