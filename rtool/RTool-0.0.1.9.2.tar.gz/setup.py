tag = '0.0.1.9.2'
from setuptools import find_packages
from distutils.core import setup
setup(
  name = 'RTool',
  packages = find_packages(),#['RTool'], # this must be the same as the name above
  version = '%s'%tag,
  description = 'A random test lib',
  author = 'Ron Nofar',
  author_email = 'ronnofar2@gmail.com',
  url = 'https://github.com/RonNofar/TextOnScreen', # use the URL to the github repo
  download_url = 'https://github.com/RonNofar/RToolPackage/archive/%s.tar.gz'%tag, # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)

#http://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
