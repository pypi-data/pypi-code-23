#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

__version__ = '0.1.0'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['docopt']
test_requirements = ['pytest']

setup(
    name='dover',
    version=__version__,
    description="A tool for tracking and incrementing project version numbering.",
    long_description=readme + '\n\n' + history,
    author="Mark Gemmill",
    author_email='dev@markgemmill.com',
    url='https://bitbucket.org/mgemmill/dover',
    packages=['dover'],
    package_dir={'dover':
                 'dover'},
    entry_points={
        'console_scripts': [
            'dover=dover.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD License",
    zip_safe=False,
    keywords='version dover',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
