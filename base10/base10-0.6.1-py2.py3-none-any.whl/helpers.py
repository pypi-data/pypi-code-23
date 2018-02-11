from base10.base import Metric
from base10.exceptions import Base10Error


class MetricHelper(Metric):
    __initialised__ = False

    def __new__(cls, *args, **kwargs):
        if not cls.__initialised__:
            kwargs = cls._pop_and_store('name', kwargs)
            kwargs = cls._pop_and_store('fields', kwargs)
            kwargs = cls._pop_and_store('metadata', kwargs)

            if 'time' in cls._fields:
                cls._fields.remove('time')

            cls.__initialised__ = True

        return super(Metric, cls).__new__(cls)

    @classmethod
    def _pop_and_store(cls, prop, kwargs):
        priv_prop = '_' + prop

        if prop in kwargs:
            setattr(cls, priv_prop, kwargs.pop(prop))
        else:
            if not hasattr(cls, priv_prop):
                raise Base10Error(priv_prop + ' is required')

        return kwargs

    def __init__(self, **kwargs):
        kwargs.pop('name', None)
        kwargs.pop('fields', None)
        kwargs.pop('metadata', None)

        self._verify_and_store(kwargs)


class MetricHandler(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_reader') and not hasattr(self, '_writer'):
            raise Base10Error('Either _reader or _writer is required')

        if not hasattr(self, '_dialect'):
            raise Base10Error('_dialect is required')

    def read(self):
        try:
            while True:
                yield self._dialect.from_string(next(self._reader.read()))
        except AttributeError as e:
            raise Base10Error(
                'Attempt to read from a write-only MetricHandler', e
            )

    def write(self, metric):
        try:
            return self._writer.write(self._dialect.to_string(metric))
        except AttributeError as e:
            raise Base10Error(
                'Attempt to write to a read-only MetricHandler', e
            )
