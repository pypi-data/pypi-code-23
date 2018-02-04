from __future__ import absolute_import
from os.path import join, dirname
from setuptools import setup
import ekuerre

basepath = dirname(__file__)
binpath = join(basepath, 'bin')

setup(
  name = 'ekuerre',
  packages = ['ekuerre'],
  version = ekuerre.__version__,
  description = 'QR web service provider',
  long_description = open(join(basepath, 'README.txt')).read(),
  scripts = [],
  install_requires=['qrcode', 'pillow'],
  author = 'Gamaliel Espinoza M.',
  author_email = 'gamaliel.espinoza@gmail.com',
  url = 'https://github.com/gamikun/ekuerre',
  keywords = ['qr', 'api', 'png'],
  classifiers = [],
)
