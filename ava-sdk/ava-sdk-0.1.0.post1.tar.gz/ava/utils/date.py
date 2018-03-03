# -*- coding: utf-8 -*-
from datetime import datetime
import rfc3339

def get_datetime_in_rfc3339(timestamp=None):
    time = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
    return rfc3339.rfc3339(time)

def get_datetime_in_underscore(_datetime=None):
    """
    get datetime string concat with underscore,
    for example: `2017_6_13_10_13_6`
    """
    _datetime = _datetime or datetime.now()
    return "_".join(map(str, list(_datetime.timetuple()))[:6])
