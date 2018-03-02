import datetime
from .base import AttributeValueVirtual, AttributeValueNull
from ..exceptions import OrmValueError


class ValueInterval(AttributeValueVirtual):
    def __init__(self):
        super(ValueInterval, self).__init__()

    def __repr__(self):
        return "[%r,%r]" % (self.low, self.high)

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def _check_value(self, value):
        c = self._get_c()
        childs_type = c.childs_type
        if value is None or isinstance(value, AttributeValueNull):
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this interval attribute is not nullable!")
            return
        if (isinstance(value, int) and childs_type not in ('int', 'float')) \
                or (isinstance(value, float) and childs_type != 'float') \
                or (isinstance(value, datetime.datetime) and childs_type != 'datetime') \
                or (isinstance(value, datetime.date) and childs_type not in ('date', 'datetime')) \
                or (isinstance(value, datetime.time) and childs_type not in ('time', 'datetime')):
            raise OrmValueError("interval values must be '%s' type!" % childs_type)
        elif not isinstance(value, (int, float, datetime.date, datetime.time, datetime.datetime)):
            raise OrmValueError("intervals can handle only numeric and date/time values!")

    @property
    def nullable(self):
        return self._get_c().nullable if self._get_c() is not None else True

    @property
    def min(self):
        return self._get_c().min_value if self._get_c() is not None else None

    @property
    def max(self):
        return self._get_c().max_value if self._get_c() is not None else None

    @property
    def low(self):
        return getattr(self.instance, self._get_c().k_low) if self._get_c() is not None else None

    @low.setter
    def low(self, value):
        self._check_value(value)
        if self.min is not None and value < self.min:
            value = self.min
        setattr(self.instance, self._get_c().k_low, value)

    @property
    def high(self):
        return getattr(self.instance, self._get_c().k_high) if self._get_c() is not None else None

    @high.setter
    def high(self, value):
        self._check_value(value)
        if self.max is not None and value > self.max:
            value = self.max
        setattr(self.instance, self._get_c().k_high, value)

    @property
    def range(self):
        return self.low, self.high

    @range.setter
    def range(self, value):
        if isinstance(value, ValueInterval):
            self.low, self.high = value.low, value.high
            return
        if value is None or isinstance(value, AttributeValueNull):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this interval attribute is not nullable!")
            self.low = None
            self.high = None
            return
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise OrmValueError("interval must be set using its low|high properties or (low,high) list/tuple!")
        self.low = value[0]
        self.high = value[1]

    def get_value(self):
        return self

    def set_value(self, instance, key, value):
        self.range = value
        return self.low, self.high

