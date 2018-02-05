#!/usr/bin/env python

from setuptools import setup, find_packages


PACKAGE = 'zcli'
DESCRIPTION = 'Simply certain useful tasks on top of the Zcash RPC interface.',

setup(
    name=PACKAGE,
    description=DESCRIPTION,
    version='0.1.1',
    author='Nathan Wilcox',
    author_email='nejucomo+dev@gmail.com',
    license='GPLv3',
    url='https://github.com/nejucomo/{}'.format(PACKAGE),
    packages=find_packages(),
    install_requires=[
        'functable >= 0.2',
        'genty >= 1.3.2',
        'pathlib2 >= 2.3.0',
        'mock >= 2.0.0',
    ],

    entry_points={
        'console_scripts': [
            '{0} = {0}.main:main'.format(PACKAGE),
        ],
    }
)
