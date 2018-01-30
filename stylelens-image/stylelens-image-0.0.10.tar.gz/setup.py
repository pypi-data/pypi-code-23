# coding: utf-8

"""
    stylelens-image

    Utility package for bl-db-image(DB)

"""


import sys
from setuptools import setup, find_packages

NAME = "stylelens-image"
VERSION = "0.0.10"
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
    description="stylelens-image",
    author_email="master@bluehack.net",
    url="",
    keywords=["BlueLens", "stylelens-image"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
