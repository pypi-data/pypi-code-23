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
    'seaborn',
    'matplotlib',
    'pandas',
    'pandas-profiling',
    'numpy',]

setup_requirements = [
    'pytest-runner',
    # TODO(eyadsibai): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='semla',
    version='0.1.0',
    description="Study, ExaMine, Learn and Analyze",
    long_description=readme + '\n\n' + history,
    author="Eyad Sibai",
    author_email='eyad.alsibai@gmail.com',
    url='https://github.com/eyadsibai/semla',
    packages=find_packages(include=['semla']),
    entry_points={
        'console_scripts': [
            'semla=semla.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='semla',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
