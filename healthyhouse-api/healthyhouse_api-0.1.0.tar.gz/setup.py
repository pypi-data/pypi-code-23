#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'marshmallow',
    'pandas'
]

setup_requirements = [
    'pytest-runner',
    # TODO(bsdis): Put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: Put package test requirements here
]

setup(
    name='healthyhouse_api',
    version='0.1.0',
    description="A wrapper of the rest API available for ha healthyhouse installation",
    long_description=readme + '\n\n' + history,
    author="Healthyhouse",
    author_email='info@radonmeters.com',
    url='https://github.com/bsdis/healthyhouse_api',
    packages=find_packages(include=['healthyhouse_api']),
    entry_points={
        'console_scripts': [
            'hh_importresults=healthyhouse_api.import_results:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='healthyhouse_api',
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
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
