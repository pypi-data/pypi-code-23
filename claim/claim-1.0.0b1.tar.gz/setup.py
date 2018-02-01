#!/usr/bin/env python3

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='claim',
    version='1.0.0b1',
    description='A cli tool for converting file\'s line endings',
    long_description=long_description,
    url='https://github.com/bukovyn/claim',
    author='bukovyn',
    author_email='bukovyn@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points = {
        'console_scripts': ['claim = claim:main']
    },
    keywords='cli converter eol end-of-line line-endings',
    py_modules=['claim'],
    python_requires='>=3'
)
