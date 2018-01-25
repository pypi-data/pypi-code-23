""" Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information. """

import sys

from setuptools import find_packages, setup
from codecs import open
from os.path import abspath, dirname, join
from emcli import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name = 'paradino',
    version = __version__,
    long_description = long_description,
    license = 'Apache 2.0',
    packages = find_packages(exclude=['tests*']),
    install_requires = [
        'docopt~=0.6.2',
        'simplejson~=3.11.1',
        'tabulate~=0.7.7',
        'future~=0.16.0',
        'semver~=2.7.7',
        'appdirs~=1.4.3',
        'progressbar2~=3.30.2',
        'clingmerv-lib==0.3.0'
    ],
    setup_requires = pytest_runner,
    tests_require = [
        'pytest~=3.0',
        'mock~=2.0.0',
        'nose~=1.3.7',
        'parameterized~=0.6.1',
        'responses~=0.5.1'
    ],
    entry_points = {
        'console_scripts': [
            'paradino=emcli.__main__:main',
        ],
    },
)

