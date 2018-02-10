###############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Start script and config
$$
"""
__docformat__ = "reStructuredText"

import sys
import logging


LOGGING_LEVELS = {
    "critical": logging.CRITICAL,
    "fatal": logging.CRITICAL,
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "notset": logging.NOTSET,
    }

def getLoggingLevel(value):
    try:
        # level is an integer or integer string
        level = int(value)
    except (ValueError, TypeError), e:
        # level is a level name
        level = str(value).lower()
        level = LOGGING_LEVELS.get(level, level)
    if level not in LOGGING_LEVELS.values():
        raise ValueError("loglevel must be on of [%s]" % ", ".join(
            LOGGING_LEVELS.values()))
    else:
        return level


class ExtraDataFormatter(logging.Formatter):
    """Formatter including extra data

    This formatter will set the extra kwargs as extra data and offers a
    data formatter variable:

    %(data)s            kibana message data

    And you can use the following variables:

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted

    """

    def format(self, record):
        """Ensure data in __dict__"""
        if not 'data' in record.__dict__:
            # ensure 'data' in __dict__
            record.__dict__['data'] = ''
        return super(ExtraDataFormatter, self).format(record)


class STDOUTFilter(logging.Filter):
    """No error message filter

    NOTE: This filter will prevent to log entries higher then level 30
    This prevents that we log the error and fatal message since we provide
    a sdterr logging handler.

    """

    def filter(self, record):
        if record.levelno > 0 and record.levelno <= 39:
            # only log DEBUG, INFO and WARN, skip ERROR and CRITICAL
            return 1
        else:
            return 0


def setUpLogger(options):
    """Setup logger using python logging

    We will setup a root logger which will handle kibana and elasticsearch
    log messages. This setup will use a stream handler usable with circus
    and log DEBUG, INFO and WARN to stdout and ERROR and CRITICAL to stderr.
    """
    # add/patch all involved loggers
    logger = logging.getLogger('')
    logger.setLevel(options.loglevel)
    if options.loglevel >= 10:
        # setup error logging handler as root logger for logging level >= 40
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.ERROR)
        formatter = ExtraDataFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(data)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # setup access logging handler as root logger for logging level (1-39)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(options.loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add filter for prevent logging ERROR and CRITICAL to stdout
        filter_ = STDOUTFilter()
        handler.addFilter(filter_)
        logger.addHandler(handler)

    if options.trace:
        # setup explict elasticsearch trace logging handler
        logger = logging.getLogger('elasticsearch.trace')
        logger.setLevel(options.loglevel)
        # setup access logging handler as root logger
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(options.loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add filter for prevent logging ERROR and CRITICAL to stdout
        filter_ = STDOUTFilter()
        handler.addFilter(filter_)
        logger.addHandler(handler)
