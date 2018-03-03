#!/usr/bin/env python

import setuptools

desc = """\
IRC3 Test Plugin
=================

Test pkg_resources plugin for irc3
"""

setuptools.setup(
    name='irc3-plugins-test',
    summary='test plugin for irc3',
    version='0.0.2',
    long_description=desc,
    author='Daniel Wallace',
    author_email='daniel@gtmanfred.com',
    url='https://github.com/gtmanfred/irc3-plugins-test',
    packages=['irc3_plugins_test',],
    entry_points='''
        [irc3.loader]
        irc3.plugins.test = irc3_plugins_test.test
    ''',
)
