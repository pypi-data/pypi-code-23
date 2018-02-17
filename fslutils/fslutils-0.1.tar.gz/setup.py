#!/usr/bin/env python
''' Installation script for fslutils package '''
import sys
from os.path import join as pjoin

# For some commands, use setuptools.
if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'install_egg_info', 'egg_info', 'easy_install', 'bdist_wheel',
            'bdist_mpkg')).intersection(sys.argv)) > 0:
    import setuptools

from distutils.core import setup

import versioneer

extra_kwargs = {}
if 'setuptools' in sys.modules:
    extra_kwargs = dict(
        zip_safe=False,
        # Check dependencies also in .travis.yml file
        requires=['numpy (>=1.8)'])


setup(name='fslutils',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Functions working with FSL outputs',
      author='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      maintainer='Matthew Brett',
      maintainer_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/fslutils',
      packages=['fslutils',
                'fslutils.tests'],
      package_data = {'fslutils': [
          'tests/data/*',
      ]},
      license='BSD license',
      classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Scientific/Engineering',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
        ],
      long_description = open('README.rst', 'rt').read(),
      **extra_kwargs
      )
