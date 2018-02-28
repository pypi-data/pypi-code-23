#!/usr/bin/env python

from distutils.core import setup

version = '0.2'

packages = ['bin']

scripts = ['bin/assemble.py', 'bin/ra2.py', 'bin/scaffolder.py']

classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 3']

requirements = ['ctbBio']

setup(name='ReAssemble',
      author='Chris Brown',
      author_email='ctb@berkeley.edu',
      packages=packages,
      scripts=scripts,
      version=version,
      license='MIT',
      url='https://github.com/christophertbrown/fix_assembly_errors',
      description='scripts for microbial genome sequence curation',
      install_requires=requirements,
      classifiers=classifiers
      )
