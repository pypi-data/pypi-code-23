#!/usr/bin/env python

from distutils.core import setup

import os


def get_version(package):
    with open(os.path.join(package, '__init__.py'), 'r') as init_py:
        for line in init_py.readlines():
            if line.startswith('__VERSION__'):
                return line[line.index('=') + 1:].strip()[1:-1]


def get_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as readme:
        return readme.read()


version = get_version('eggs')

setup(
    name='eggs',
    version=version,
    description='Simple Python3 Packages Manager',
    long_description=get_readme(),
    author='Wei Huang',
    author_email='h.wei@outlook.com',
    url='https://github.com/egg3/eggs',
    download_url='https://github.com/egg3/eggs/archive/{0}.tar.gz'.format(version),
    packages=['eggs'],
    keywords=['packages', 'manager', 'wrapper'],
    entry_points={
        'console_scripts': [
            'eggs = eggs.__main__:main'
        ]
    }
)
