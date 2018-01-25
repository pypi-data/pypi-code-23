#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import moustache

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
    name='Moustache.beta',
    version=moustache.__version__,
    python_requires='>=3',
    packages=find_packages(),
    author="Libriciel SCOP",
    author_email="hackathon@libriciel.coop",
    description="Module Moustache pour fusion ODT",
    long_description=long_description,
    install_requires=[
        'flask',
        'secretary',
        'wand'
    ],
    include_package_data=True,
    url='https://gitlab.libriciel.fr/libriciel/hackathon-2018-01/moustache',
    entry_points={
        'console_scripts': [
            'moustache = moustache:launch'
        ],
    },
    license="CeCILL v2",
)
