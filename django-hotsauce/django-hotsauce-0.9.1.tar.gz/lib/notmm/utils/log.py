#!/usr/bin/env python
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
# <LICENSE=ISC>
"""Basic logging utilities"""
import logging

__all__ = ['configure_logging', 'LOGGING_ERROR_LOG']

LOGGING_ERROR_LOG = '/var/log/django.log'

def configure_logging(logger, level=10, error_log=LOGGING_ERROR_LOG, handler=logging.FileHandler):
    logging.basicConfig(format='%(levelname)s:%(message)s', 
        level=logging.DEBUG)
    logger.addHandler(handler(error_log))
    
    return logger
