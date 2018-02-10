#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
setup(
  name = 'qserious',
  # packages=find_packages(exclude=['contrib', 'docs', 'tests/*']),
  packages=['qserious'],
  version = '0.2.6',
  description = 'query string serializer/deserializer',
  author = 'Jesus Germade',
  author_email = 'jesus@germade.es',
  url = 'https://github.com/pyKilt/qserious', # use the URL to the github repo
  # download_url = 'https://github.com/peterldowns/mypackage/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['querystring', 'query', 'string', 'serializer', 'deserializer', 'serialize', 'deserialize'], # arbitrary keywords
  classifiers = [],
  license='MIT',
)
