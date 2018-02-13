#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# zeus: file.py
#
# Define zeus file tools
#
# Copyright (C) 2016-2017, Christophe Fauchard
# -----------------------------------------------------------------

"""
Submodule: zeus.file

File and directory manipulation

Copyright (C) 2016-2017, Christophe Fauchard
"""

import os
import zeus


class Path():

    """
    manipulate paths
    - recursive path create
    - archive path with date create
    """

    def __init__(self, path):
        self.path = path
        self.create(path)

    def create(self, path):
        if os.path.exists(path) or path == "":
            return(True)
        else:
            if not (os.path.exists(os.path.dirname(path))):
                self.create(os.path.dirname(path))
            os.mkdir(path)


class DayArchivePath(Path):

    """
    Create archive paths (format base/AAAA/MM/JJ)
    """

    def __init__(self, path):
        path = zeus.date.Date().path_date_tree(path)
        zeus.file.Path.__init__(self, path)


class Log():

    """
    Log Class with switch and level capabilities
    """

    def __init__(self,
                 file_name,
                 number=10,
                 size=1,
                 frequence=None,
                 ):

        self.file_name = file_name
        self.frequence = frequence
        self.number = number
        self.size = size

        self.fd = open(self.file_name, "a")

    def print(self, text):
        print(text, file=self.fd)

    def close(self):
        self.fd.close()
