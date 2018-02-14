"""
pyspooler
"""

import os
from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pyspooler",
    version="0.1.1",
    author="Shir0kamii",
    author_email="shir0kamii@gmail.com",
    description="Python spooler",
    long_description=read("README.rst"),
    url="https://github.com/Shir0kamii/pyspooler",
    download_url="https://github.com/Shir0kamii/pyspooler/tags",
    platforms="any",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
