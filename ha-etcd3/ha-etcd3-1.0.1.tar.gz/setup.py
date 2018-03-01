#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-03-01
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import os
from setuptools import setup

setup(
    name = 'ha-etcd3',
    version = '1.0.1',
    license = 'MIT',
    description = 'high-available lib for single point of failure',
    keywords = 'ha failover single',
    url = 'https://pypi.python.org/pypi/ha-etcd3',
    author = 'Lafite93',
    author_email = '227337844@qq.com',
    classifiers = ['License :: OSI Approved :: MIT License',
                   'Development Status :: 3 - Alpha',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.5',
                  ],
    py_modules = ['etcd3ctl'],
)
