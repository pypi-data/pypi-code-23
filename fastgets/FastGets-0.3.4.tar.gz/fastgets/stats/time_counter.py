# coding: utf8
import datetime
from ..core.client import get_client


class TimeCounter(object):

    time_format = None
    interval = None

    @classmethod
    def generate_key(cls, name, current):
        return 'time:{name}:{current}'.format(
            name=name,
            current=current.strftime(cls.time_format)
        )

    @classmethod
    def parse_current(cls, key):
        current_str = key.split(':')[-1]
        return datetime.datetime.strptime(current_str, cls.time_format)

    @classmethod
    def incr(cls, name, field='default', current=None, num=1, pipe=None):
        client = pipe or get_client()
        if not current:
            current = datetime.datetime.now()
        key = cls.generate_key(name, current)
        client.hincrby(key, field, amount=num)

    @classmethod
    def get_count(cls, name, current=None, field='default'):
        current = current or datetime.datetime.now()
        key = cls.generate_key(name, current)
        val = get_client().hget(key, field)
        return int(val or 0)

    @classmethod
    def get_counts(cls, name, start=None, end=None, num=60):
        if start and end:
            num = int((end - start).total_seconds() / cls.interval) + 1
        elif start and not end:
            end = start + datetime.timedelta(seconds=cls.interval * num)
        elif not end:
            end = datetime.datetime.now()
        counts = []
        currents = []
        while num > 0:
            key = cls.generate_key(name, end)
            currents.append(cls.parse_current(key))
            dct = get_client().hgetall(key) or {}
            counts.append({k: int(v) for k, v in dct.items()})
            end -= datetime.timedelta(seconds=cls.interval)
            num -= 1
        counts = list(zip(currents, counts))
        counts.reverse()
        return counts


class SecondCounter(TimeCounter):

    time_format = '%Y%m%d%H%M%S'
    interval = 1


class MinuteCounter(TimeCounter):

    time_format = '%Y%m%d%H%M'
    interval = 60


class DayCounter(TimeCounter):

    time_format = '%Y%m%d'
    interval = 86400
