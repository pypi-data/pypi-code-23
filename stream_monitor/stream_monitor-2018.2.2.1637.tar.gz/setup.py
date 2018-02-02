#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import setuptools

def main():

    setuptools.setup(
        name             = "stream_monitor",
        version          = "2018.02.02.1637",
        description      = "monitoring and alerting program for data streams such as recording files that update regularly",
        long_description = long_description(),
        url              = "https://github.com/wdbm/stream_monitor",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        py_modules       = [
                           "stream_monitor"
                           ],
        install_requires = [
                           "docopt",
                           "propyte",
                           "tonescale"
                           ],
        scripts          = [
                           "stream_monitor.py"
                           ],
        entry_points     = """
                           [console_scripts]
                           stream_monitor = stream_monitor:stream_monitor
                           """
    )

def long_description(
    filename = "README.md"
    ):

    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
