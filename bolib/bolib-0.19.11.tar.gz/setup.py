# -*- coding: utf-8 -*-
#
#    Copyright 2018 Ibai Roman
#
#    This file is part of BOlib.
#
#    BOlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BOlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BOlib. If not, see <http://www.gnu.org/licenses/>.

import os.path
import setuptools


def read(file):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, file), 'r') as f:
        return f.read()

setuptools.setup(
    name='bolib',
    version='0.19.11',
    author='Ibai Roman',
    author_email='ibaidev@users.noreply.github.com',
    description=('Python library for Bayesian Optimization.'),
    license='GPLv3',
    keywords='Bayesian Optimization Gaussian Process',
    url='https://github.com/ibaidev/bolib',
    long_description=read('README.rst'),
    packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests']),
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
        'gplib',
        'numpy',
        'scipy',
        'matplotlib'
    ]
)
