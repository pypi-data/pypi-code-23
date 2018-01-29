# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

install_requires = [
    'Jinja2 >= 2.10',
    'PyYAML >= 3.12',
]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'configrender'))

setup(
    name='configrender',
    packages=['configrender'],
    version='1.0.5',
    description='Config Render',
    author='afon',
    author_email='me@afon.ninja',
    url='https://dev.afon.ninja/',
    install_requires=install_requires,
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': [
            'configrender=configrender.render:main'
        ],
    }
)
