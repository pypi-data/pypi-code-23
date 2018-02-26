#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'numpy',
    'IPython',
    'typing',
    # TODO: Put package requirements here
]

setup_requirements = [
    # TODO(francois-durand): Put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: Put package test requirements here
]

setup(
    name='hanabython',
    version='0.1.5',
    description="A Python implementation of Hanabi, a game by Antoine Bauza",
    long_description=readme + '\n\n' + history,
    author="François Durand",
    author_email='fradurand@gmail.com',
    url='https://github.com/francois-durand/hanabython',
    # packages=find_packages(include=['hanabython']),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hanabython=hanabython.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='hanabython',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
