import calendar
import numbers
from datetime import datetime

import pytz
import six
import sys
import time
from dateutil.parser import parse
from dateutil.tz import tzutc
from tzlocal import get_localzone


def to_milliseconds(date):
    """
    :param date: None | `str` in iso format | :class:`datetime` | `int`
    :return: timestamp in milliseconds
    """
    if date is None:
        return int(time.time() * 1000)

    if isinstance(date, numbers.Number):
        return date

    elif isinstance(date, (six.binary_type, six.text_type)):
        dt = parse(date)
    elif isinstance(date, datetime):
        dt = date
    else:
        raise ValueError('time should be either number, datetime instance or str')
    dt_utc = timezone_ensure(dt).astimezone(tzutc())
    ms = (calendar.timegm(dt_utc.timetuple()) + dt_utc.microsecond / 1000000.0) * 1000
    return ms


def to_date(time):
    """
    :param time: `str` in iso format | `int` | :class:`datetime`
    :return: datetime
    """
    if time is None:
        return None

    if isinstance(time, datetime):
        return timezone_ensure(time)
    elif isinstance(time, (six.binary_type, six.text_type)):
        date = parse(time)
    elif isinstance(time, numbers.Number):
        date = pytz.utc.localize(datetime.utcfromtimestamp(time * 0.001))
    else:
        raise ValueError('time should be either datetime instance, str or number')
    return timezone_ensure(date)


def to_iso(date):
    """
    :param date: :class:`datetime` | `str`
    :return: `str`
    """
    if date is None:
        return None

    if isinstance(date, (six.binary_type, six.text_type)):
        return date

    if date.tzinfo is None:
        date = get_localzone().localize(date)
    microsecond = date.microsecond
    millisecond = int(microsecond / 1000)
    iso = date.isoformat().replace('.{:06d}'.format(microsecond), '.{:03d}'.format(millisecond))

    return iso


def timezone_ensure(datetime_obj, tz=get_localzone()):
    """
    :param datetime_obj: datetime object'
    :param tz: _datetime.tzinfo
    :return: datetime instance
    """
    if datetime_obj.tzinfo is None:
        return tz.localize(datetime_obj)
    else:
        return datetime_obj.astimezone(tz)


def timediff_in_minutes(prev_date, next_date=None):
    """
    Return time difference in minutes.
    If prev_date is not specified return sys.maxsize
    If next_date is not specified, next_date is set to current time.
    :param prev_date: None | iso `str` | :class:`datetime` | `int`
    :param next_date: None | iso `str` | :class:`datetime` | `int`
    :return: time difference in minutes
    """
    if prev_date is None:
        return sys.maxsize
    else:
        prev_date = to_date(prev_date)

    if next_date is None:
        next_date = get_localzone().localize(datetime.now())
    else:
        next_date = to_date(next_date)

    prev_date_date_ts = time.mktime(timezone_ensure(prev_date).timetuple())
    next_date_ts = time.mktime(timezone_ensure(next_date).timetuple())

    return int(next_date_ts - prev_date_date_ts) / 60
