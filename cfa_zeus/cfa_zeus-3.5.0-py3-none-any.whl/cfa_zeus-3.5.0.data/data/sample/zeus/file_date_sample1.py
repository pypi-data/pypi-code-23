#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# zeus: file_date_sample1.py
#
# test date manipulation
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import zeus

now = zeus.date.Date()

print(now.date_iso())
print(now.date_time_iso())
print(now.path_date_tree('tmp'))
now.print()
print("message")