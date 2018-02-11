import abc
import six
from time import time

from base10.exceptions import DialectError


class Metric(object):
    """Generic Metric class
    """

    def __init__(self, name, fields, metadata, **kwargs):
        """Create a new Metric
        
        :param name: Name of the metric.
        :param fields: List of field names to include.
        :param metadata: List of metadata field names to include.
        :param **kwargs: Keyword values for the fields and metadata.
        """
        self._name = name
        self._fields = fields
        self._metadata = metadata

        if 'time' in self._fields:
            self._fields.remove('time')

        self._verify_and_store(kwargs)

    def _verify_and_store(self, values):
        timestamp = values.pop('time', self._current_timestamp())

        if sorted(self._fields + self._metadata) != sorted(values.keys()):
            raise NameError(
                'Expected {} but got {}'.format(
                    sorted(self._fields + self._metadata),
                    sorted(values.keys())
                )
            )

        self._values = values
        self._values['time'] = timestamp

    def _current_timestamp(self):
        return time() * 1000

    @property
    def name(self):
        """Get Metric name
        """
        return self._name

    @property
    def fields(self):
        """Get Metric fields
        """
        return self._fields

    @property
    def metadata(self):
        """Get Metric metadata
        """
        return self._metadata

    @property
    def values(self):
        """Get Metric values
        """
        return self._values

    def __repr__(self):
        return '<Metric:"{}" Fields:{} Metadata:{} Values:{}>'.format(
            self.name, self.fields, self.metadata, self.values
        )


class Dialect(object):
    def __init__(self, *args, **kwargs):
        pass

    def from_string(self, string):
        raise DialectError('Attempt to read with a write-only dialect')

    def to_string(self, metric):
        raise DialectError('Attempt to write with a read-only dialect')


@six.add_metaclass(abc.ABCMeta)
class Reader(object):
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def read(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class Writer(object):
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def write(self, string):
        pass
