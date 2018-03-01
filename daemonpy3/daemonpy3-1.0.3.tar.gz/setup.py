#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-03-01
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import os
from setuptools import setup

setup(
    name = 'daemonpy3',
    version = '1.0.3',
    license = 'MIT',
    description = 'Turn any command line into a daemon with a pidfile',
    long_description = open(os.path.join(os.path.dirname(__file__),
                                         'README.md')).read(),
    keywords = 'daemon python cli init nohup commandline executable script pidfile',
    entry_points={'console_scripts': ['daemoncmd = daemoncmd:main']},
    url = 'https://github.com/todddeluca/daemoncmd',
    author = 'Todd Francis DeLuca',
    author_email = 'todddeluca@yahoo.com',
    classifiers = ['License :: OSI Approved :: MIT License',
                   'Development Status :: 3 - Alpha',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.5',
                  ],
    py_modules = ['daemonize'],
)

