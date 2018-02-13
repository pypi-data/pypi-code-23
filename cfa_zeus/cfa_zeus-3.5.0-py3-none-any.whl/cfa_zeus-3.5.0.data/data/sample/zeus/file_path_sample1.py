#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# zeus: file_path_sample1.py
#
# test file path manipulation
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import zeus

print("version zeus: " + zeus.__version__)

path = zeus.file.Path("tmp/rep1/rep2/rep3")
archive_path = zeus.file.DayArchivePath("tmp/archive")
