#!/usr/bin/env python

import re
from setuptools import setup, find_packages

from codecs import open
from os import path

pkg_name = 'pyampio'

here = path.abspath(path.dirname(__file__))
version_file = 'version.py'

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, pkg_name, 'version.py'), encoding='utf-8') as f:
    data = f.read()

    match = re.search("__version__ = '([^']+)'", data)
    assert match, 'Cannot find version number in {} package'.format(pkg_name)
    version = match.group(1)

setup(name=pkg_name,
      version=version,
      description='A Python Ampio Server USB<->CAN',
      long_description=long_description,
      url='http://github.com/kstaniek/pyampio',
      author='Klaudiusz Staniek',
      author_email='kstaniek@gmail.com',
      license='Apache 2.0',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: System :: Hardware :: Hardware Drivers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      packages=find_packages(exclude=['tests']),
      keywords='ampio automation can',
      install_requires=['pyserial>=3.1.1', 'pyserial-asyncio==0.4', 'PyYAML==3.12', 'voluptuous==0.11.1', 'click==6.7'],
      include_package_data=True,
      data_files=[('pyampio', ['pyampio/modules.yaml'])],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'ampio = pyampio.__main__:cli',
          ]
      }
)
