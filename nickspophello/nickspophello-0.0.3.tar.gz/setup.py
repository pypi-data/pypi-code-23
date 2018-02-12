#!/usr/local/bin/env python3
from setuptools import setup
from hello import __version__


with open('README.rst') as f:
    readme = f.read()
with open('CHANGES.rst') as f:
    changes = f.read()


setup(
    name='nickspophello',  # The name of the package
    version=__version__,  # The version number of the package
    description='a module / utility to print Hello World.',
    long_description=readme + '\n\n' + changes,
    author='Nick Cresner',  # The maintainer
    author_email='nickcresner@gmail.com',  # Their author_email
    url='https://github.com/nickcresner/helloWorld.py.git',
    py_modules=['hello', ],
    licence='MIT',
    entry_points={
        'console_scripts': ['hello=hello:main'],
    }
)
