#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import PPM_Common

setup(

    name='PPM_Common',

    version=PPM_Common.__version__,

    packages=find_packages(exclude=['databaseconnexion','classconfig', 'exception','json','test']),

    author="Fanny",

    author_email="fanny.esposito@histofig.com",

    description="Tools for connection to mongodDB et Elasticsearch",

    long_description=open('README.md').read(),

    install_requires= ["bson","pymongo","elasticsearch>=6.0.0,<7.0.0"],

    include_package_data=True,

    url='https://github.com/Histofig/PPM_Common',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
	"Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)

