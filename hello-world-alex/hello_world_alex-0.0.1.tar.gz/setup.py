#!/usr/bin/env python 3
from setuptools import setup
from hello import __version__

with open('README.rst') as f:
  readme = f.read()
with open('CHANGES.rst') as f:
  changes = f.read()


setup(
  name='hello_world_alex',
  version=__version__,
  description='An utility to display a name',
  long_description=readme + '\n\n' + changes,
  author='Alex Cwiek',
  author_email='alex@wegotpop.com',
  url='https://github.com/alexcviek/hello_world_alex',
  py_modules=['hello', ],
  license='MIT',
  entry_points={'console_scripts': ['hello=hello:main'],}
  )