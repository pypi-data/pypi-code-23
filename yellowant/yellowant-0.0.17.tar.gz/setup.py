#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

__author__ = 'Vishwa Krishnakumar <vishwa@yellowant.com>'
__version__ = '0.0.17'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='yellowant',
    version=__version__,
    install_requires=['requests>=2.1.0', 'requests_oauthlib>=0.4.0', 'click'],
    author='Vishwa Krishnakumar',
    author_email='vishwa@yellowant.com',
    license=open('LICENSE').read(),
    url='https://github.com/vishwa306/yellowant-python-sdk/tree/master',
    keywords='yellowant slack bot',
    description='Python wrapper for the YellowAnt API',
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ],
    entry_points={
        "console_scripts": [
            "yellowant=yacli.cli:cli"
        ],
    }
)
