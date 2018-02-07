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
    # TODO: put package requirements here
    'requests>=1.0.0',
    'six>=1.0.0',
    'marshmallow>=1.0.0'
]

setup_requirements = [
    # TODO(livingmine): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
    'nose'
]

setup(
    name='midtrans_python_rest_sdk',
    version='0.1.7',
    description="Midtrans Python REST SDK",
    long_description=readme + '\n\n' + history,
    author="Muhammad Irfan",
    author_email='irfan@rubyh.co',
    url='https://github.com/livingmine/midtrans_python_rest_sdk',
    packages=find_packages(include=['midtrans_python_rest_sdk']),
    entry_points={
        'console_scripts': [
            'midtrans_python_rest_sdk=midtrans_python_rest_sdk.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='midtrans_python_rest_sdk',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
