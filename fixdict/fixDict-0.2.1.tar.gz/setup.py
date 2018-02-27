#!/usr/bin/env python
from setuptools import setup

VERSION = '0.2.1'
DESCRIPTION = "fix_dict: fix your dict and insert it into MongoDB"
LONG_DESCRIPTION = """
Removes dots "." from keys, as mongo doesn't like that.

Also, convert ints more than 8-bytes  to string cause BSON can only handle up to 8-bytes ints.

Finaly, your lovely MongoDB can accept your dict and store it.

"""

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
]

setup(
    name="fixDict",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=('dict',
              'python',
              'mongodb',
              'data srtucture',
              'transform',
              'fix',
              'fix dict',
              'remove dot'),
    author="Ryan Luo",
    author_email="luo_senmu@163.com",
    url="https://github.com/Senmumu/fixdict",
    license="MIT License",
    platforms=['any'],
    test_suite="",
    zip_safe=True,
    install_requires=[],
    packages=['fixdict']
)
