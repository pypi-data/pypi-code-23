#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# zeus: __init__.py
#
# Copyright (C) 2016-2017, Christophe Fauchard
# -----------------------------------------------------------------

"""
Module: zeus

general usage toolbox

Copyright (C) 2016-2017, Christophe Fauchard
"""


import sys
from zeus._version import __version__, __version_info__

__author__ = "Christophe Fauchard <christophe.fauchard@gmail.com>"

if sys.version_info < (3, 5):
    raise RuntimeError('You need Python 3.5+ for this module.')

import zeus.file
import zeus.parser
import zeus.exception
import zeus.crypto
import zeus.date
import zeus.log
