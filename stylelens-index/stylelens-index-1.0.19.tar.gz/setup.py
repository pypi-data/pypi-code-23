# coding: utf-8

"""
    stylelens-index

    Utility package for bl-db-index(DB)

"""


from setuptools import setup, find_packages

NAME = "stylelens-index"
VERSION = "1.0.19"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["python-dateutil", "pymongo"]

setup(
    name=NAME,
    version=VERSION,
    description="stylelens-index",
    author_email="master@bluehack.net",
    url="",
    keywords=["BlueLens", "stylelens-index"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
