# -*- coding: utf-8 -*-
import setuptools

setuptools.setup(
    name="sqlite_ucf",
    version="1.0.1",
    author="Tim Mitchell",
    author_email="tim.mitchell@seequent.com",
    description="An alternate sqlite3.connect function that adds unicode case folding functionality.",
    license="BSD",
    keywords="sqlite unicode",
    url="https://github.com/tim-mitchell/sqlite_ucf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
    ],
)
