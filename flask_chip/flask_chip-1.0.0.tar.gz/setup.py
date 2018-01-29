#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Flask>=0.10.1',
    'Werkzeug>=0.10.4',
    'itsdangerous>=0.24',
    'blinker>=1.3',
    'six>=1.7.3',
    'toolz>=0.8.2',
    'pyresult>=1.0.1',
]

test_requirements = [
    'coverage',
    'flake8',
    'pytest',
    'pytest-cov',
    'tox',
    'mock',
]

setup(
    name='flask_chip',
    version='1.0.0',
    description="A token generator for Flask apps.",
    long_description=readme + '\n\n' + history,
    author="Jindrich K. Smitka",
    author_email='smitka.j@gmail.com',
    url='https://github.com/s-m-i-t-a/flask_chip',
    packages=[
        'flask_chip',
    ],
    package_dir={'flask_chip':
                 'flask_chip'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='flask_chip',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
