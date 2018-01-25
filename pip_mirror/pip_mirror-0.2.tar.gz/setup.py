#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from pip_mirror import version
from setuptools import setup

setup(name='pip_mirror',
      version=version,
      description='Mirroring tool that implements a local pip mirror via PyPi',
      long_description=open('README.md').read(),
      author='Ian Maguire',
      author_email='mr.scalability@gmail.com',
      license = 'Creative Commons version 4.0',
      url='https://github.com/ianmaguire/pip_mirror',
      packages=['pip_mirror'],
      scripts=['scripts/pip_mirror', 'scripts/processlogs', 'scripts/pip_mirror_check_files'],
      keywords = ['pip', 'mirror', 'pep381', 'bandersnatch'],
      classifiers = [],
     )
