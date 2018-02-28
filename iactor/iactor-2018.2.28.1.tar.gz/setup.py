# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2018-02-28 14:44:05
# @Last Modified 2018-02-28
# @Last Modified time: 2018-02-28 14:47:56

from distutils.core import setup
import sys

version = '2018.2.28.1'

setup(
  name = 'iactor',
  packages = ['iactor'], # this must be the same as the name above
  install_requires = ["generators", "strict_functions"],
  version = version,
  description = 'High performance actor model for python functions and coroutines',
  author = 'Cody Kochmann',
  author_email = 'kochmanncody@gmail.com',
  url = 'https://github.com/CodyKochmann/iactor',
  download_url = 'https://github.com/CodyKochmann/iactor/tarball/{}'.format(version),
  keywords = ['iactor', 'actor', 'iter', 'coroutines', 'async', 'parallel', 'actors', 'thread'],
  classifiers = [],
)
