#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('dev-requirements.txt') as f:
    test_requirements = f.read().splitlines()


setup(
    name='netuitive_statsd',
    version='0.3.4',
    description="Netuitive StatsD server",
    long_description='Netuitive StatsD server\n',
    author="Netuitive",
    author_email='python@netuitive.com',
    url='https://github.com/netuitive/netuitive-statsd',
    install_requires=requirements,
    license="Apache License 2.0",
    zip_safe=False,
    keywords='netuitive netuitive-statsd',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    packages=['libs', 'libs.statsd', ''],
    scripts=['netuitive-statsd']
)
