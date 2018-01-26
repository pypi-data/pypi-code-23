# coding: utf-8

"""
    A Python implementation of Telestream Cloud REST interface

    Contact: cloudsupport@telestream.net
"""


import sys
from setuptools import setup, find_packages

NAME = "telestream-cloud"
VERSION = "2.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["telestream-cloud-qc>=2", "telestream-cloud-flip>=2", "telestream-cloud-tts>=2"]

setup(
    name=NAME,
    version=VERSION,
    description="A Python implementation of Telestream Cloud REST interface",
    author_email="cloudsupport@telestream.net",
    url="",
    keywords=["TCS", "Telestream"],
    install_requires=REQUIRES,
    long_description="""\
    A Python implementation of Telestream Cloud REST interface
    """
)
