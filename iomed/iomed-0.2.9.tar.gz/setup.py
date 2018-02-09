#!/usr/bin/env python3
from setuptools import setup

setup(name='iomed',
      version='0.2.9',
      description='cli to IOMED Medical Language API',
      author='IOMED Medical Solutions SL',
      author_email='dev@iomed.es',
      url='https://github.com/iomedhealth/pyomed',
      packages=['iomed'],
      entry_points={
          'console_scripts': [
              'iomed = iomed.__main__:main',
          ],
      },
      install_requires=['requests', 'argparse', 'squid>=0.0.3']
      )
