from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'cayenneLPP',
  packages = ['cayenneLPP'],
  version = '0.5b3',
  description = 'A module for the Cayenne Low Power Packet format',
  long_description=long_description,
  license = 'MIT',
  author = 'Johan Barthelemy',
  author_email = 'johan@uow.edu.au',
  url = 'https://github.com/jojo-/py-cayenne-lpp',
  keywords = ['Cayenne', 'Low Power Payload', 'LPP'],
  classifiers = ['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: Implementation :: MicroPython']
)
