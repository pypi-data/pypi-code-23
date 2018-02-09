#! /usr/bin/env python

from setuptools import setup

import versioneer

setup(name = 'ioamdoit',
      description = 'common ioam doit tasks',
      version = versioneer.get_version(),
      cmdclass = versioneer.get_cmdclass(),
      license = 'MIT',
      url = 'http://github.com/ioam/ioamdoit',
      packages=['ioamdoit'],
      install_requires=['doit']
      )
