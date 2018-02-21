#!/usr/bin/env python
"""
Installs the Wagtail readinglevel plugin that adds reading level check
functionality to rich text editors.This helps when trying to create content
that conforms to the WCAG 2.0
"""

from setuptools import setup, find_packages

setup(name='wagtail-readinglevel',
      version='2.0',
      description='Determine reading age of a piece of text.',
      url='http://github.com/vixdigital/wagtail-readinglevel',
      author='VIX Digital',
      author_email='info@vix.digital',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'wagtail>=1.0',
      ],
      zip_safe=False)
