#!/usr/bin/env python

from setuptools import setup, find_packages


PACKAGE = 'writefile'

setup(
    name=PACKAGE,
    description='Write stdin to a path, creating directories as necessary.',
    version='0.2',
    author='Nathan Wilcox',
    author_email='nejucomo@gmail.com',
    license='GPLv3',
    url='https://github.com/nejucomo/{}'.format(PACKAGE),

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            '{0} = {0}.main:main'.format(PACKAGE),
        ],
    }
)
