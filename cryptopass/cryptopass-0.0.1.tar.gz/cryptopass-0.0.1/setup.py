#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 17:57:11 2018

@author: f2a
"""

from setuptools import setup


setup(
      name='cryptopass',        # This is the name of your PyPI-package.
      version='0.0.1',            # Update the version number for new releases
      author='f2a',
      scripts=['cryptopass'],    # The name of your scipt, and also the command you'll be using for calling it
      description='Safe passwords manager'
      )
