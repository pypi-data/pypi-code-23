#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: huay
# Mail: imhuay@163.com
# Created Time:  2018-1-26 11:33:13
#############################################

from setuptools import setup, find_packages

setup(
    name="huaytools",
    version="0.1.11",
    keywords=("huay", "huaytools"),
    description="huay's tools",
    long_description="huay's tools",
    license="MIT Licence",

    url="https://github.com/imhuay/huaytools",
    author="huay",
    author_email="imhuay@163.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['six', 'bs4']
)
