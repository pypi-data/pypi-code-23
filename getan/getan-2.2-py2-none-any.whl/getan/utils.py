# -*- coding: utf-8 -*-
#
# (c) 2008, 2009, 2010 by
#   Sascha L. Teichmann <sascha.teichmann@intevation.de>
#   Ingo Weinzierl <ingo.weinzierl@intevation.de>
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging

global DATETIME_FORMAT
DATETIME_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

logger = logging.getLogger()


def human_time(seconds):
    if seconds is None or seconds == 0:
        return "--:--:--"
    s = seconds % 60
    seconds /= 60
    m = seconds % 60
    seconds /= 60
    out = "%02d:%02d:%02d" % (seconds, m, s)
    return out


def safe_int(s, default=0):
    try:
        return int(s)
    except ValueError:
        return default


def short_time(seconds):
    if seconds is None:
        logger.warn(
            "short_time(): No seconds given to format to 'short_time'.")
        return "0:00h"
    seconds /= 60
    m = seconds % 60
    seconds /= 60
    return "%d:%02dh" % (seconds, m)


def format_datetime(datetime):
    return datetime.strftime(DATETIME_FORMAT)


def format_time(datetime):
    return datetime.strftime(TIME_FORMAT)
