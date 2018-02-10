#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, RuntimeError):
    long_description = open('README.md').read()

setup(name='bitwallet',
      version='1.0.7',
      packages=find_packages(),
      install_requires=[
          'ccxt',
          'requests',
          'pandas',
          'pyyaml',
          'coinbase'
      ],
      description='Python Wallet that enables P&L',
      long_description=long_description,
      author='Dimitrios Kouzis-Loukas',
      author_email='lookfwd@gmail.com',
      url='https://github.com/lookfwd/bitwallet',
      scripts=['bin/bitwallet'],
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
          'Development Status :: 5 - Production/Stable',
          'Topic :: Office/Business :: Financial',
      ],
      test_suite="bitwallet.tests")
