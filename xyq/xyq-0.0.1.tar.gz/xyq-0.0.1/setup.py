#!/usr/bin/env python

import glob
from setuptools import setup, find_packages

tests_require = ["coverage", "flake8", "wheel"]

setup(
    name="xyq",
    version="0.0.1",
    url="https://github.com/kislyuk/xyq",
    license="Apache Software License",
    author="Andrey Kislyuk",
    author_email="kislyuk@gmail.com",
    description="xyq",
    long_description=open("README.rst").read(),
    install_requires=[
    ],
    tests_require=tests_require,
    extras_require={"test": tests_require},
    packages=find_packages(exclude=["test"]),
    scripts=glob.glob("scripts/*"),
    include_package_data=True,
    test_suite="test",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
