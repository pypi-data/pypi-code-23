#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Guilherme Caminha",
    author_email='gpkc@cin.ufpe.br',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    description="A cython compiler for compiling source code in string form.",
    install_requires=['cython', 'numpy'],
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='cypyler',
    name='cypyler',
    packages=find_packages(include=['cypyler']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/gpkc/cypyler',
    version='0.2.0',
    zip_safe=False,
)
