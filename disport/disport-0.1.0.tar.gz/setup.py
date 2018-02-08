# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="disport",
    version="0.1.0",
    description="A xrandr wrapper",
    license="MIT",
    author="Tim Wunderlich",
    author_email="mail@tim-wunderlich.de",
    url="https://github.com/TimWunderlich/disport",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points = {
        "console_scripts": ['disport = disport.disport:main']
        },
)
