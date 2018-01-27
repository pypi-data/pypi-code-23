import os
from distutils.core import setup
import easyIoCtl.start as start
setup(
  name = 'easyIoCtl',
  packages = ['easyIoCtl'], # this must be the same as the name above
  version = '1.0',
  description = 'Abstractions away from boring IO operations',
  author = 'Austin Glover',
  author_email = 'dev_genuis@sphyreye.com',
  url = 'https://github.com/AustinGlover/EasyIoCtl', # use the URL to the github repo
  download_url = 'https://github.com/AustinGlover/EasyIoCtlarchive/1.0.tar.gz', # I'll explain this in a second
  keywords = ['testing', 'logging', 'memory'], # arbitrary keywords
  classifiers = [],
)
