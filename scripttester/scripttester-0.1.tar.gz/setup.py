#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Installation script for scripttester package '''
import re

import setuptools
from distutils.core import setup

import versioneer

# Get install requirements from requirements.txt file
with open('requirements.txt', 'rt') as fobj:
    install_requires = [line.strip() for line in fobj
                        if line.strip() and not line[0] in '#-']
# Get any extra test requirements
with open('test-requirements.txt', 'rt') as fobj:
    test_requires = [line.strip() for line in fobj
                     if line.strip() and not line[0] in '#-']

# Requires for distutils (only used in pypi interface?)
break_ver = re.compile(r'(\S+?)(\[\S+\])?([=<>!]+\S+)')
requires = [break_ver.sub(r'\1 (\3)', req) for req in install_requires]

cmdclass = versioneer.get_cmdclass()

setup(name='scripttester',
      version=versioneer.get_version(),
      cmdclass=cmdclass,
      description='Utility for testing command line scripts',
      author='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      maintainer='Matthew Brett',
      maintainer_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/scripttester',
      packages=['scripttester'],
      package_data = {'scripttester': [
          'tests/*.py',
          'tests/mypkg66/*.py',
          'tests/mypkg66/mypkg66/*',
          'tests/mypkg66/scripts/*']},
      license='BSD license',
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
        ],
      long_description = open('README.rst', 'rt').read(),
      extras_require = {'test': test_requires}
      )
