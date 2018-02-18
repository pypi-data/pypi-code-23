#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <python_jsonschema_objects - An object wrapper for JSON Schema definitions>
# Copyright (C) <2018-2018>  Chris Wacek <cwacek@gmail.com

from setuptools import setup, find_packages

setup(name='flask-bourbon',
      description='Flask + Bourbon makes you swagger',
      author='Chris Wacek',
      license="MIT",
      author_email='cwacek@gmail.com',
      packages=find_packages(),
      zip_safe=False,
      use_scm_version=True,
      setup_requires=["setuptools>=18.0.0", 'setuptools_scm'],
      install_requires=[
          "python-jsonschema-objects~=0.3.2",
          "flask"
      ],
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Intended Audience :: Developers',
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent'
      ]
      )
