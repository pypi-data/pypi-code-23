# coding: utf-8

"""
    bluelens-k8s

    Contact: master@bluehack.net
"""


import sys
from setuptools import setup, find_packages

NAME = "bluelens-k8s"
VERSION = "0.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = []

setup(
    name=NAME,
    version=VERSION,
    description="A utility for Kubernetes",
    author_email="master@bluehack.net",
    url="",
    keywords=["BlueLens", "bluelens-k8s"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
