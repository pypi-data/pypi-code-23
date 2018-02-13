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
    # TODO: Put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(GudarJs): Put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: Put package test requirements here
]

setup(
    name='teacv',
    version='0.1.0',
    description="teacv is a tool for extend Python OpenCV modules with custom filters written in C++.",
    long_description=readme + '\n\n' + history,
    author="Guzmán D. Darío",
    author_email='guzman.d.dario@gmail.com',
    url='https://github.com/GudarJs/teacv',
    packages=find_packages(include=['teacv']),
    entry_points={
        'console_scripts': [
            'teacv=teacv.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='teacv',
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
