#!/usr/bin/python3
# -*- coding: utf8 -*-

from distutils.core import setup
from pip.req import parse_requirements

setup(
  name='liberate',
  version='0.1.5',
  description='Video/Audio/Url liberation (to .ogg)',
  author='Nichlas Severinsen',
  author_email='ns@nsz.no',
  url='https://notabug.org/necklace/liberate',
  packages=['liberate'],
  include_package_data=True,
  package_data={'liberate': ['requirements.txt']},
  scripts=['liberate/liberate'],
  install_requires=parse_requirements('requirements.txt', session='hack')
)
