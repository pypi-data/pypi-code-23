import logging

from .util import get_timestamp

logger = logging.getLogger(__name__)


class Counter(object):

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[],
                 sign=None):

        self.name = name
        self.metricType = 'GAUGE'
        self.orgtype = ['COUNTER']
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

    def add_value(self, value, ts, rate=None, sign=None):
        self.timestamp = get_timestamp()

        if rate is None:
            rate = 1.0

        if sign == '+':
            self.signed = True
            self.samples.append(float(value) * float(rate))
        elif sign == '-':
            self.samples.append(float(-value) * float(rate))
        else:
            self.samples.append(float(value) * float(rate))

    def get_values(self, timestamp):

        samlen = len(self.samples)

        if samlen > 0:

            self.cnt = float(samlen)
            self.sum = sum(self.samples)
            self.samples.sort()

            if len(self.samples) > 0:
                self.min = float(self.samples[0])
            else:
                self.min = float(0)

            if len(self.samples) > 1:
                self.max = float(self.samples[-1])
            else:
                self.max = self.min

            self.avg = float(self.sum / self.cnt)

        else:
            self.value = float(0)
            self.min = None
            self.max = None
            self.avg = None
            self.sum = float(0)
            self.cnt = float(0)

        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': self.sum,
                'avg': self.avg,
                'cnt': self.cnt,
                'max': self.max,
                'min': self.min,
                'sum': self.sum
            }
        }

        return(ret)

    def clear(self):
        self.value = float(0)
        self.samples = []
        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = float(0)
