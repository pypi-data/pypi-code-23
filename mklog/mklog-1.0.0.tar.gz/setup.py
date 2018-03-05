#!/usr/bin/env python3

# Copyright 2014-2015 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Installer"""

from setuptools import setup, find_packages
import codecs
import os

def readme():
    """Return content of file `./README.rst`."""
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    with codecs.open(
        os.path.join(directory, "README.rst"),
        encoding="utf8",
        mode="r",
        errors="replace",
        ) as file:
        return file.read()

setup(
    name='mklog',
    version="1.0.0",
    packages=find_packages(exclude=["test*"]),
    setup_requires=["hgtools"],
    install_requires=[
        ],
    include_package_data=True,
    author='Louis Paternault',
    author_email='spalax+python@gresille.org',
    description='Append date and time before text',
    url='http://git.framasoft.org/spalax/mklog',
    license="GPLv3 or any later version",
    test_suite="test.suite",
    entry_points={
        'console_scripts': ['mklog = mklog.__main__:main']
        },
    keywords = "log timestamp",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Logging",
    ],
    long_description=readme(),
    zip_safe=True,
)
