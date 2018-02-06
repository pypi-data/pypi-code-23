#!/usr/bin/env python3

from distutils.core import setup
from glob import glob
from os.path import basename, splitext
from subprocess import check_output

# from setuptools import find_packages

setup(author='Maryke van der Walt',
      author_email='mvanderwalt@westmont.edu',
      description='Utilities to draw and manipulate a subdivision curve',
      # install_requires=['numpy','matplotlib'],
      license='LGPL',
      name='westmont-subdiv',
      py_modules = ['draw_utils'],
      version='0.1'
      # use_scm_version=True,
      # setup_requires=['setuptools_scm']
      )
