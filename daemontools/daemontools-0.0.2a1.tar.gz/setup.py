#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='daemontools',
    version='0.0.2.alpha1',
    description='Daemonizing and single instance tools.',
    long_description=long_description,
    url='https://github.com/medovarsky/daemon-tools',
    author="Lubos Medovarsky",
    author_email="lubos@medovarsky.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        ],
    keywords=['daemon', 'single', 'instance'],
    zip_safe=True,
    packages=['daemontools'],
    python_requires='>=2.6'
    )

