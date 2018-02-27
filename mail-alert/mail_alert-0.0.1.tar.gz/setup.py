#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

setup(
    name = "mail_alert",
    version = "0.0.1",
    keywords = ("pip", "email"),
    description = "monitor project and send email when errors occur",
    long_description = "monitor project and send email when errors occur",
    license = "MIT Licence",

    url = "",
    author = "yaolu",
    author_email = "yaolu0405@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
