import logging

from .util import get_timestamp

logger = logging.getLogger(__name__)


class Histogram(object):

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
        self.metricType = 'GAUGE'
        self.orgtype = ['TIMER', 'HISTOGRAM']
        self.timestamp = get_timestamp()
        self.rate = 1
        self.percentile = 0
        self.samples = []
        self.value = float(0)
        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = float(0)

    def add_value(self, value, ts):
        timestamp = get_timestamp()

        self.value += value
        self.samples.append(value)
        self.timestamp = timestamp

    def get_values(self, timestamp):

        samlen = len(self.samples)

        if samlen > 0:
            self.cnt = samlen
            self.samples.sort()
            self.sum = sum(self.samples)
            self.min = float(self.samples[0])
            self.max = float(self.samples[-1])
            self.avg = float(sum(self.samples) / int(samlen))

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
        self.samples = []
        self.min = None
        self.max = None
        self.avg = None
        self.sum = None
        self.cnt = float(0)
        self.value = float(0)
