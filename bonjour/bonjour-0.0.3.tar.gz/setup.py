#!/usr/bin/env python3
from setuptools import setup
from bonjour import __version__

with open('readme.rst') as f:
    readme = f.read()
with open('CHANGES.rst') as f:
    changes = f.read()

setup(
    # The name of the package
    name='bonjour',
    # The number of the version for the package
    version=__version__,
    # A short description of the package
    description='A module / utility to say hello to you in French.',
    # description description (displayed on PyPI's page for the package)
    long_description=readme + '\n\n' + changes,
    # The maintainer
    author='Emilie',
    # Thei email
    author_email='emilie@wegotpop.com',
    # The package's website
    url='https://github.com/Em774/bonjour_monde',
    # The Python modules to include
    py_modules=['bonjour', ],
    # The license type
    license='MIT',
    # Helpful classifications / metadata
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
    # Links the "bonjour" command with a function to call
    entry_points={
        'console_scripts': ['bonjour=bonjour:main'],
    }
)
