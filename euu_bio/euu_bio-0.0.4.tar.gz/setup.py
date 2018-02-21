#! /usr/bin/env python
#################################################################################
#     File Name           :     setup.py
#     Created By          :     qing
#     Creation Date       :     [2018-02-16 10:04]
#     Last Modified       :     [2018-02-21 10:33]
#     Description         :      
#################################################################################

from distutils.core import setup
setup(
  name = 'euu_bio',
  packages = ['euu_bio', 'euu_bio.tool'], # this must be the same as the name above
  version = '0.0.4',
  description = 'A Python Bio Toolkit',
  author = 'Qing Ye',
  author_email = 'qingye3@illinois.edu',
  url = 'https://github.com/qingye3/euu_bio', # use the URL to the github repo
  download_url = '', # I'll explain this in a second
  keywords = ['bio', 'toolkit', ''], # arbitrary keywords
  classifiers = [],
)


