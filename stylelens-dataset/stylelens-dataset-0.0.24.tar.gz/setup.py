# coding: utf-8

"""
    stylelens-dataset

    Utility package for bl-db-dataset(DB)

"""


import sys
from setuptools import setup, find_packages

NAME = "stylelens-dataset"
VERSION = "0.0.24"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["pymongo"]

setup(
    name=NAME,
    version=VERSION,
    description="stylelens-dataset",
    author_email="master@bluehack.net",
    url="",
    keywords=["BlueLens", "stylelens-dataset"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
