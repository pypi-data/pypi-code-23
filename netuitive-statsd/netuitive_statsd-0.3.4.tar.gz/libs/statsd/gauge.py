import logging

from .util import get_timestamp

logger = logging.getLogger(__name__)


class Gauge(object):

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.metricType = 'GAUGE'
        self.orgtype = ['GAUGE']
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
        self.value = float(0)
        self.signed = False
        self.timestamp = get_timestamp()
        self.samples = []
        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = float(0)

    def add_value(self, value, ts, sign=None):
        self.timestamp = get_timestamp()

        if sign is None:
            self.value = float(value)

        if sign == '+':
            self.signed = True
            self.value += float(value)

        if sign == '-':
            self.signed = True
            self.value += float(-value)

        self.samples.append(self.value)

    def get_values(self, timestamp):

        samlen = len(self.samples)

        if samlen > 0:
            self.cnt = samlen
            self.sum = sum(self.samples)
            self.samples.sort()
            self.min = float(self.samples[0])
            self.max = float(self.samples[-1])
            self.avg = float(self.sum / self.cnt)

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': self.value,
                'avg': self.avg,
                'cnt': self.cnt,
                'max': self.max,
                'min': self.min,
                'sum': self.sum
            }
        }

        return(ret)

    def clear(self):
        # make sure we keep the last value
        self.samples = [self.value]
        self.value = float(0)

        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = float(0)
