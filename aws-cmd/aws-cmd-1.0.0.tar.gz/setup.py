#!/usr/bin/env python

from distutils.core import setup

setup(
    # Application name:
    name="aws-cmd",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="Steven hk Wong",
    author_email="steven@wongsrus.net",

    # Packages
    packages=["aws-cmd"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/aws-cmd_v1.0.0/",

    #
    license="LICENSE.txt",
    description="Simple AWS cli.",

    long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "boto3",
    ],
)
