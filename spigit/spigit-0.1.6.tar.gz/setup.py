#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
import setuptools
from setuptools.command.install import install
from distutils.core import setup
import sys
import os

def get_requirements():
    """Load list of dependencies."""

    install_requires = []
    with open("requirements/project.txt") as f:
        for line in f:
            if not line.startswith("#"):
                install_requires.append(line.strip())
    return install_requires

LONG_DESC = '''
spigit is a python service that keeps a deployment repo up-to-date.
It uses GitPython and requires python 2.7.
You can learn more about using spigit by `reading the docs`_.
.. _`reading the docs`: http://username.github.io/spigit/
Support
=======
Help and support is available here at the repository's `issues`_.
.. _`issues`: https://github.com/username/spigit/issues
'''

setup(
    name='spigit',
    version='0.1.6',
    keywords='github git server deployment service update',
    description='A deployment manager service.',
    long_description=LONG_DESC,
    author='Taylor Halcomb',
    author_email='taylortextalert@gmail.com',
    url='https://github.com/username/spigit/',
    packages=['spigit'],
    install_requires=get_requirements(),
    package_data = {
        '': ['*'],
    },
    data_files=[('spigit', ['spigit/gitscriptconfig.json', 'spigit/service', 'spigit/serviceinstall.sh']),
    ],
    zip_safe=False,
    license='MIT'
)
