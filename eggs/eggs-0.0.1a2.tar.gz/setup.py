#!/usr/bin/env python

from distutils.core import setup

version = '0.0.1a2'

setup(
    name='eggs',
    version=version,
    description='Simple Python3 Packages Manager',
    author='Wei Huang',
    author_email='h.wei@outlook.com',
    url='https://github.com/egg3/eggs',
    download_url='https://github.com/egg3/eggs/archive/{0}.tar.gz'.format(version),
    packages=['eggs'],
    keywords=['packages', 'manager', 'wrapper'],
)