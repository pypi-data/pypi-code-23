#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from setuptools import setup
import sys

sys.path.insert(0, '.')
import version

setup(name='si-prefix',
      version=version.getVersion(),
      description='Functions for formatting numbers according to SI standards.',
      keywords='si prefix format number precision',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/cfobel/si-prefix',
      license='BSD-3',
      packages=['si_prefix', 'si_prefix.tests'])
