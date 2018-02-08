# -*- coding: utf-8 -*-
#
#    Copyright 2018 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.rst')) as f:
    LDESC = f.read()

setup(
    name='gplib',
    version='0.5.10',
    author='Ibai Roman',
    author_email='ibaidev@users.noreply.github.com',
    description=('Python library for Gaussian Process Regression.'),
    license='GPLv3',
    keywords='Gaussian Process',
    url='https://github.com/ibaidev/gplib',
    long_description=LDESC,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    install_requires=[
        'scipy',
        'numpy',
        'matplotlib'
    ]
)
