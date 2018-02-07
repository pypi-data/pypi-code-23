#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
import os

base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "src")

# Add the src/ directory to the sys.path
sys.path.insert(0, src_dir)

about = {}
with open(os.path.join(src_dir, "inventorpy", "__version__.py")) as f:
    exec(f.read(), about)

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'flask',
    'bcrypt',
    'sqlalchemy',
    'sqlalchemy_utils',
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__url__'],
    py_modules=[about['__title__']],
    long_description=readme,
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
