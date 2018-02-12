#!/usr/local/bin/env python3
from setuptools import setup
from hello import __version__

with open('README.rst') as f:
    readme = f.read()
with open('CHANGES.rst') as f:
    changes = f.read()

setup(
name='nickspophello', # The name of the package
version=__version__, # The version number of the package
description='a module / utility to print Hello World or the name of the user.', #A long description #(displayed on PyPi's page for the package)
long_description=readme + '\n\n' + changes,
author='Nick Cresner', #The maintainer
author_email='nickcresner@gmail.com', #Their author_email
url='https://github.com/nickcresner/helloWorld.py.git', #The package's website
py_modules=['hello',], # The Python modules to include
licence='MIT', #The licence type
    entry_points={ #links the 'hello' command with a function to call
    'console_scripts': ['hello=hello:main'],
     }
)
