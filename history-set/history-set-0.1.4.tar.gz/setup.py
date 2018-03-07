#!/usr/bin/env python3
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

setup(name='history-set',
      version="0.1.4",
      description='A Set implementation that tracks added and removed elements.',
      packages=find_packages('lib'),
      package_dir={'': 'lib'},
      author='Dave Lundgren, Connor Riva, Tjaart van der Walt',
      author_email='dlungren@outsideopen.com, criva@westmont.edu, tjaart@outsideopen.com',
      url='https://bitbucket.org/westmont/history_set',
      py_modules=[splitext(basename(path))[0] for path in glob('lib/*.py')],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      setup_requires=['setuptools-markdown'],
      long_description_markdown_filename='README.md',
      )
