"""Cryptocurrency tracker"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cryptotax',
    version='1.0a1',
    description='Cryptocurrency tracker',
    long_description=long_description,
    author='Amol Bhave',
    author_email='ammubhave@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Financial',
    ],
    keywords='bitcoin cryptocurrency tax',
    packages=find_packages(),
    extras_require={
        'dev': ['pre-commit'],
    })
