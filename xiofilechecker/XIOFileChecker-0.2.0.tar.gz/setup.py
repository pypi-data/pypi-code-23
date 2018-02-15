#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from XIOFileChecker.utils.constants import VERSION

setup(name='XIOFileChecker',
      version=VERSION,
      description='Tool to compare XIOS input and output',
      author='Levavasseur Guillaume',
      author_email='glipsl@ipsl.fr',
      url='https://github.com/prodiguer/IOCheck',
      packages=find_packages(),
      include_package_data=True,
      python_requires='>=2.7, <3.0',
      platforms=['Unix'],
      zip_safe=False,
      entry_points={'console_scripts': ['XIOFileChecker=XIOFileChecker.XIOFileChecker:run']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Natural Language :: English',
                   'Operating System :: Unix',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Build Tools']
      )
