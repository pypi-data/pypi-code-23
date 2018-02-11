from six import string_types

from base10.base import Dialect
from base10.exceptions import DialectError


class InfluxDBDialect(Dialect):
    def to_string(self, metric):
        name = self._clean_measurement(metric.name)
        tags = [
            '{}={}'.format(self._clean_tag_key(k), self._clean_tag_value(v))
            for k, v in sorted(metric.values.items()) if k in metric.metadata
        ]
        fields = [
            '{}={}'.format(
                self._clean_field_key(k), self._clean_field_value(v)
            ) for k, v in sorted(metric.values.items()) if k in metric.fields
        ]
        timestamp = metric.values['time']

        return '{}{}{} {} {:d}'.format(
            name, ','
            if len(tags) > 0 else '', ','.join(tags), ','.join(fields),
            int(timestamp * 1e6)
        )

    def _clean_measurement(self, measurement):
        if isinstance(measurement, string_types):
            measurement = measurement.replace(',', '\\,')
            measurement = measurement.replace(' ', '\\ ')
        return measurement

    def _clean_tag_key(self, key):
        if isinstance(key, string_types):
            key = key.replace(',', '\\,')
            key = key.replace('=', '\\=')
            key = key.replace(' ', '\\ ')
        return key

    def _clean_tag_value(self, value):
        if isinstance(value, string_types):
            value = value.replace(',', '\\,')
            value = value.replace('=', '\\=')
            value = value.replace(' ', '\\ ')
        return value

    def _clean_field_key(self, key):
        if isinstance(key, string_types):
            key = key.replace(',', '\\,')
            key = key.replace('=', '\\=')
            key = key.replace(' ', '\\ ')
        return key

    def _clean_field_value(self, value):
        if isinstance(value, string_types):
            return '"{}"'.format(value)
        return value
