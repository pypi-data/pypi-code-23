from __future__ import division

import logging
from datetime import datetime

import pytz

from .settings import LOGORAMA_TZ


class DateTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ts = record.created * 1000000000
        dt = datetime.fromtimestamp(ts // 1000000000, tz=pytz.utc)
        dt = dt.astimezone(tz=pytz.timezone(LOGORAMA_TZ))
        s = "{}.{}".format(
            dt.strftime("%Y-%m-%d %H:%M:%S"), int(ts % 1000000000))
        return s