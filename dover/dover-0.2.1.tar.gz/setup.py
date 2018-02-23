#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
from setuptools import setup
from setuptools import find_packages
from os.path import basename, splitext

__version__ = '0.2.1'

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
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(i))[0] for i in glob("src/*.py")],
    entry_points={
        'console_scripts': [
            'dover=dover.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD License",
    zip_safe=False,
    keywords='project version versioning dover',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
