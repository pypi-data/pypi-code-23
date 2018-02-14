#!/usr/bin/env python

from distutils.core import setup

description = 'This is demo to show how to created the private modules.'

setup(
    name='cc-password',
    version='1.0',
    description='Module for password utilities',
    maintainer='Causecode',
    maintainer_email='hardik.desai@causecode.com',
    url='http://www.causecode.com',
    long_description=description,
    packages=['cc-password']
)
