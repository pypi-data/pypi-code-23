#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="EnforsML",
    version="0.0.3",
    author="Christer Enfors",
    author_email="christer.enfors@gmail.com",
    url="https://github.com/enfors/EnforsML",
    license="LGPL",
    description="A very small set of tools used for things related to "
    "machine learning.",
    packages=find_packages(),
    install_requires=["pillow"],
    python_requires=">=3",

)
