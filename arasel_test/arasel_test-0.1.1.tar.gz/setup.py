#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'dill>=0.2.7.1', 'pandas>=0.22.0', 'flask==0.12.2', 'flask-sqlalchemy==2.3.2']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Alberto Egido",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    data_files=[('data', ['data/model.dill', 'data/orders.csv'])],
    description="Test Solution to TransfCustomer Lifetime Value for each customer in input CSV.",
    entry_points={
        'console_scripts': [
            'arasel_test=arasel_test.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='arasel_test',
    name='arasel_test',
    packages=find_packages(include=['arasel_test']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/bertucho/arasel_test',
    version='0.1.1',
    zip_safe=False,
)
