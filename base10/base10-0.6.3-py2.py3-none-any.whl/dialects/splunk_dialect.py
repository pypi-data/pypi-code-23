from base10.base import Dialect
from base10.exceptions import DialectError


class SplunkDialect(Dialect):
    def to_string(self, metric):
        pairs = ['metric_name={}'.format(self._clean_value(metric.name))]
        pairs += [
            '{}={}'.format(self._clean_key(k), self._clean_value(v))
            for k, v in metric.values.items() if k != 'time'
        ]
        timestamp = int(metric.values['time'])

        return '{:d} {}'.format(timestamp, ','.join(pairs))

    def _clean_key(self, key):
        key = key.replace('"', '')
        key = key.replace('\'', '')
        key = key.replace(' ', '_')
        return key

    def _clean_value(self, value):
        if isinstance(value, basestring):
            value = value.replace('"', '\\"')
            value = '"{}"'.format(value)
        return value
