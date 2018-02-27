#!/usr/bin/env python
from setuptools import setup

VERSION = '1.1.0'
DESCRIPTION = "Dict2obj: transform dict to simpler object"
LONG_DESCRIPTION = """
Dict2obj is a Python implementation to transform python dict to object,thus you 
can access json with easier way "dot",I'm sure this little tool can save your life.
"""

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
]

setup(
    name="dict2obj",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=('dict',
              'python',
              'object',
              'data srtucture',
              'transform',),
    author="Ryan Luo",
    author_email="luo_senmu@163.com",
    url="https://github.com/Senmumu/dict2obj",
    license="MIT License",
    platforms=['any'],
    test_suite="",
    zip_safe=True,
    install_requires=[],
    packages=['dict2obj']
)
