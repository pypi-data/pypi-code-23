import logging

from .util import get_timestamp

logger = logging.getLogger(__name__)


class Set(object):

    def __init__(self, name, sparseDataStrategy='None', unit='', tags=[]):
        self.name = name
        self.sparseDataStrategy = sparseDataStrategy
        self.unit = unit
        self.tags = tags
        self.values = []
        self.timestamp = get_timestamp()
        self.metricType = 'GAUGE'
        self.orgtype = ['SET']

    def add_value(self, value, ts, sign=None):

        timestamp = get_timestamp()
        if value not in self.values:
            self.values.append(value)

        self.timestamp = timestamp

    def get_values(self, timestamp):

        value = float(len(self.values))
        ret = {
            self.name: {
                'timestamp': timestamp,
                'value': value
            }
        }

        return(ret)

    def clear(self):
        self.values = []
