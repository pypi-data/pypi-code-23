#!/usr/bin/env python3
from setuptools import setup
from hello1234 import __version__

with open('README.rst') as f:
    readme = f.read()
with open('CHANGES.rst') as f:
    changes = f.read()

setup(
    name='hello1234',  # The name of the packages
    version=__version__,  # The version number of the package
    # A short description of the package
    description='A module / utility to greet people.',
    # a long description (displayed on PyPi's page for the package)
    long_description=readme + '\n\n' + changes,
    author='Nora Denes',  # The maintainer
    author_email='denes.nori@yahoo.com',  # Their email
    url='https://github.com/denesnori/helloworld1234',  # the package's website
    py_modules=['hello1234', ],  # The python module to include
    licence='MIT',  # The licence type
    include_package_data=True,
    classifiers=[  # Helpful classifications / metadata
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
    ],
    entry_points={  # Links 'hello1234' command with a function to call
        'console_scripts': ['hello1234=hello1234:main']
    }
)
