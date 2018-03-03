#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Standard Library
import codecs
import os

from setuptools import find_packages
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='websauna.tests',
    version='1.0a8',
    url='https://github.com/websauna/websauna.tests',
    author='Mikko Ohtamaa',
    author_email='mikko@opensourcehacker.com',
    maintainer='Erico Andrei',
    maintainer_email='erico@tokenmarket.net',
    license='MIT',
    keywords='pyramid pytest websauna',
    description='Test fixtures for Websauna',
    long_description=read('README.rst'),
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['websauna', ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pyramid',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    install_requires=[
        'codecov',
        'flake8',
        'flaky',
        'isort',
        'plaster',
        'pyramid',
        'pytest-cov',
        'pytest-runner',
        'pytest-splinter',
        'pytest-timeout',
        'pytest>=3.1.1',
        'sqlalchemy',
        'transaction',
        'websauna.system',  # Needs to be added
        'webtest',
    ],
    extras_require={
        # Dependencies needed to build and release Websauna
        'dev': [
            'pyroma==2.2',  # This is needed until version 2.4 of Pyroma is released
            'sphinx>=1.6.1',
            'sphinx-autodoc-typehints',
            'sphinx_rtd_theme',
            'sphinxcontrib-zopeext',
            'zest.releaser[recommended]'
        ],
    },
    entry_points={
        'pytest11': [
            'websauna = websauna.tests.fixtures',
        ],
    },
)
