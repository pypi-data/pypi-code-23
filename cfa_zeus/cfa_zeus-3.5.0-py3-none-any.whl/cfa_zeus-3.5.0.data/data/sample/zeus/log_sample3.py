#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# zeus: log_sample3.py
#
# log testing, rotation by date and Log class use
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import sys
import logging
import zeus

log = zeus.log.Log("./tmp/log_sample3.log", frequence='m')
log.logger.info("%s %s", "test", "test2")