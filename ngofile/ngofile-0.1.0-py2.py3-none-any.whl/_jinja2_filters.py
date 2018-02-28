# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pathlib
from builtins import object
from builtins import str


# add a custom filter to retrieve creation date
def created(path):
    import datetime
    if isinstance(path, pathlib.Path):
        return datetime.datetime.utcfromtimestamp(path.stat().st_ctime)
    return datetime.datetime.utcfromtimestamp(os.path.getctime(path))


# add a custom filter for formating dates
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)
