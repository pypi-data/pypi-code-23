#!/usr/bin/env python3
from setuptools import setup
from bonjour import __version__

with open('readme.rst') as f:
    readme = f.read()
with open('CHANGES.rst') as f:
    changes = f.read()

setup(
    name='bonjour', #The name of the package
    version=__version__, #The number of the version for the package
    description='A module / utility to say hello to you in French.', #A short description of the package
    long_description=readme + '\n\n' +changes, #description description (displayed on PyPI's page for the package)
    author='Emilie', # The maintainer
    author_email='emilie@wegotpop.com', #Thei email
    url='https://github.com/ntoll/bonjour_monde', #The package's website
    py_modules=['bonjour',], # The Python modules to include
    license='MIT', #The license type
    classifiers=[ #Helpful classifications / metadata
        'Development Status :: 4 - Beta',
    ],
    entry_points={ #Links the "bonjour" command with a function to call
        'console_scripts': ['bonjour=bonjour:main'],
    }
)
