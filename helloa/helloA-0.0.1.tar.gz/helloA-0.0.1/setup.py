#!/usr/bin/env python3

from setuptools import setup
from hello import __version__

with open('README.rst') as f:
  readme = f.read()
with open('CHANGES.rst') as f:
  changes = f.read()

setup(
  name='helloA', # The name of the package
  version=__version__, # The version number for the package
  # A short description of the package
  description='A module / utility to say Hello World',
  # A long description (displayed on PyPi's page for the package)
  long_description=readme + '\n\n' + changes,
  author='Ansi Britto', # The maintainer
  author_email='ansi@wegotpop.com', # Their email
  url='https://github.com/ArockiaAnsi/hello_world_A', # The package's website
  py_modules=['helloA', ], # The python modules to include
  license='MIT', # The license type
  entry_points={ # Links the "hello" command witha function to call
    'console_scripts': ['helloA=hello:main'],
  }
)
