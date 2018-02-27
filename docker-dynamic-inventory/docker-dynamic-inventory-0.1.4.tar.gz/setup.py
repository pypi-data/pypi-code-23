#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import os

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as reqs_file:
    requirements = reqs_file.readlines()

with open('requirements_dev.txt') as reqs_file:
    dev_requirements = reqs_file.readlines()

setup(
    author="Shaun Martin",
    author_email='shaun@samsite.ca',
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
    description="Outputs a dynamic inventory of Docker containers for Ansible.",
    entry_points={
        'console_scripts': [
            'docker-dynamic-inventory=docker_dynamic_inventory.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='docker-dynamic-inventory',
    name='docker-dynamic-inventory',
    packages=find_packages(include=['docker_dynamic_inventory']),
    setup_requires=requirements,
    test_suite='tests',
    tests_require=dev_requirements + requirements,
    url='https://github.com/inhumantsar/python-docker-dynamic-inventory',
    version='0.1.4',
    zip_safe=False,
)
