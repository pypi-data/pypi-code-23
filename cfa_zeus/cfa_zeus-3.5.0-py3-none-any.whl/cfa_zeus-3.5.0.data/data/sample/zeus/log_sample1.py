#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# zeus: log_sample1.py
#
# log testing, rotation by size
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import sys
import logging
import logging.handlers

#
# create the logger
#
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#
# create formatter log
#
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

#
# first handler for a size based log file (size in bytes)
#
file_handler = logging.handlers.RotatingFileHandler('tmp/file_log_sample1.log', 'a', 100, 1)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
file_handler.setLevel(logging.DEBUG)

#
# second handler for the console
#
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
stream_handler.setLevel(logging.DEBUG)

#
# testing the log
#
logger.info('Hello')
logger.warning('Testing %s', 'foo')