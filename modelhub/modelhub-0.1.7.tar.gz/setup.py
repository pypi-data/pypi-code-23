#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

try:
    README = open('README.md').read()
except Exception:
    README = ""
VERSION = "0.1.7"
TF_REQUIRE_VERSION = "1.4.0"

requirments = ["click", "boto3", "appdirs", "grpcio", "pyyaml", "six"]

from distutils.version import LooseVersion
import pkg_resources

try:
    tf_pkg = pkg_resources.get_distribution("tensorflow")
except pkg_resources.DistributionNotFound:
    try:
        tf_pkg = pkg_resources.get_distribution("tensorflow-gpu")
    except pkg_resources.DistributionNotFound:
        tf_pkg = None

if not tf_pkg:
    requirments.append("tensorflow")
elif LooseVersion(tf_pkg.version) < TF_REQUIRE_VERSION:
    requirments.append(tf_pkg.key + ">=" + TF_REQUIRE_VERSION)

if sys.version_info.major < 3:
    requirments += ["configparser", "pathlib"]

setup(
    name='modelhub',
    version=VERSION,
    description='Modelhub',
    url="http://git.patsnap.com/research/modelhub",
    long_description=README,
    author='Jay Young(yjmade)',
    author_email='yangjian@patsnap.com',
    packages=find_packages(),
    install_requires=requirments,
    extras_require={
        "tf_serving": ["redis"]
    },
    entry_points={
        'console_scripts': [
            'modelhub=modelhub.commands:main'
        ]
    },
)
