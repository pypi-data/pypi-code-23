#!/usr/bin/env python3
from setuptools import setup
from hello import __version__

with open('README.rst') as f:
    readme = f.read()

with open('CHANGES.rst') as f:
    changes = f.read()

setup(
    name='charlie_pop_hello',  # name of package
    version=__version__,  # version number of package
    # A short description of the package
    description=' A module to say hello',
    # A long description displayed on PyPi
    long_description=readme + '\n\n' + changes,
    author='Charlie Allatson',  # The maintainer
    author_email='charles.allatson@gmail.com',  # Their email
    url='https://github.com/charlieallatson/hello_world',  # package's website
    py_modules=['hello', ],  # The python modules to include
    license='MIT',  # The license type
    entry_points={  # Links the "hello" command with a function to call
        'console_scripts': ['hello=hello:main'],
    }
)
