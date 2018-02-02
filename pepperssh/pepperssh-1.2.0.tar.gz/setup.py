#!/usr/bin/env python

from distutils.core import setup

VERSION = '1.2.0'

setup(
    name='pepperssh',
    description='Simple SSH based remote execution',
    version=VERSION,
    package_dir={'': 'src'},
    packages=['pepperssh'],
    author='Michael Kleehammer',
    author_email='michael@kleehammer.com',
    url='https://gitlab.com/mkleehammer/pepperssh'
)
