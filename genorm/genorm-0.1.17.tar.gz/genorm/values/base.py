import datetime
from ..exceptions import OrmNotDefinedYet
from ..utils import str2datetime, str2date, str2time


def wrap_value(model, instance, c, key, value, textual=False):
    from ..funcs import RequestTableBelongedColumn
    if type(value) is AttributeValueNull:
        value = None
    if isinstance(c, RequestTableBelongedColumn):
        c = c.c
    value_class = getattr(c, 'value_class', None)
    value_handler = getattr(c, 'value_handler', None)
    if value_handler is not None:
        value = value_handler(value)
    if value_class is not None and not (textual and isinstance(value, str)):
        if AttributeValueAbstract in value_class.mro():
            if value_class.basecls is not False:
                if value is None and not c.nullable:
                    value = c.default
                value = value_class.new(value) if value is not None else AttributeValueNull()
            else:
                value = value_class.new(value)
        else:
            value = value_class(value)
        value.model = model
        value.model_k = key
        value.instance = instance
        value.c = c
    elif isinstance(value,
                    (str, int, float, bytes, bool, tuple, list, datetime.date, datetime.time, datetime.datetime)) \
            or value is None:
        if isinstance(value, str):
            value_class = AttributeValueString
        elif isinstance(value, int):
            value_class = AttributeValueInteger
        elif isinstance(value, float):
            value_class = AttributeValueFloat
        elif isinstance(value, bytes):
            value_class = AttributeValueBinary
        elif isinstance(value, bool):
            value_class = AttributeValueBoolean
        elif isinstance(value, datetime.datetime) \
                and not isinstance(value, datetime.date) \
                and not isinstance(value, datetime.time):
            value_class = AttributeValueDateTime
        elif isinstance(value, datetime.date):
            value_class = AttributeValueDate
        elif isinstance(value, datetime.time):
            value_class = AttributeValueTime
        else:
            value_class = AttributeValueNull
        value = value_class.new(value)
        value.model = model
        value.model_k = key
        value.instance = instance
        value.c = c
    return value


class AttributeValueAbstract(object):
    """ Abstract class for attribute value representation types """
    basecls = None
    check_modified = True

    def __init__(self, *args, **kwargs):
        self.model = None
        self.model_k = None
        self.instance = None
        self.c = None

    @classmethod
    def new(cls, value):
        """ Calls by ORM mechanics right after creating the class'es instance. """
        return cls(value)

    def initialize(self, key, value):
        self.c.initialize(self.instance, key, value)

    @property
    def caption(self):
        return self.c.caption

    @property
    def abbreviation(self):
        return self.c.abbreviation

    @property
    def options(self):
        return self.c.options

    @property
    def string(self):
        if not hasattr(self, 'text_repr'):
            return str(self.base(self))
        return self.text_repr(self.base(self))

    def base(self, value):
        if self.basecls is None or isinstance(self.basecls, bool):
            return None
        return self.basecls(value)

    @property
    def value(self):
        return self.base(self)

    def __repr__(self):
        r = self.string
        return str(r) if not isinstance(r, str) else r

    def text_repr(self, value):
        if not hasattr(self.c, 'text_repr'):
            return str(value)
        r = self.c.text_repr(value, instance=self.instance)
        return "" if r is None else str(r)

    def log_repr(self, src, dst):
        return self.c.log_repr(src, dst, instance=self.instance)

    def call_on_change(self, src, dst):
        self.c.call_on_change(src, dst)

    def verify(self, value):
        return self.c.verify(value)


class AttributeValueNull(AttributeValueAbstract):
    """ Representation of 'NULL' value ('None' in Python terms) """
    basecls = None

    @classmethod
    def new(cls, value):
        return cls()

    @property
    def string(self):
        return self.text_repr(None)

    def base(self, value):
        return None

    @property
    def value(self):
        return None

    def __repr__(self):
        return "<NULL>"

    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

    def log_repr(self, src, dst):
        return self.c.log_repr(src, dst, instance=self.instance)

    def on_change(self, src, dst):
        self.c.on_change(src, dst)

    def verify(self, value):
        return self.c.verify(value)


class AttributeValueString(AttributeValueAbstract, str):
    basecls = str


class AttributeValueBinary(AttributeValueAbstract, bytes):
    basecls = bytes


class AttributeValueBoolean(AttributeValueAbstract, int):
    basecls = int

    @property
    def value(self):
        return bool(self.base(self))

    def __str__(self):
        return "True" if self.value else "False"


class AttributeValueInteger(AttributeValueAbstract, int):
    basecls = int


class AttributeValueFloat(AttributeValueAbstract, float):
    basecls = float


class AttributeValueDate(AttributeValueAbstract, datetime.date):
    basecls = datetime.date

    def base(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            return None
        elif isinstance(value, (datetime.datetime, datetime.date)):
            return datetime.date(value.year, value.month, value.day)
        elif isinstance(value, str):
            try:
                v_ = str2date(value)
            except ValueError:
                return None
            return datetime.date(v_.year, v_.month, v_.day)
        return None

    @classmethod
    def new(cls, value):
        if value is None:
            return AttributeValueNull()
        if isinstance(value, (datetime.datetime, datetime.date)):
            return cls(value.year, value.month, value.day)
        elif isinstance(value, str):
            try:
                v_ = str2date(value)
            except ValueError:
                return AttributeValueNull()
            return cls(v_.year, v_.month, v_.day)
        return AttributeValueNull()


class AttributeValueTime(AttributeValueAbstract, datetime.time):
    basecls = datetime.time

    def base(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            return None
        elif isinstance(value, (datetime.datetime, datetime.time)):
            return datetime.time(value.hour, value.minute, value.second)
        elif isinstance(value, str):
            try:
                v_ = str2time(value)
            except ValueError:
                return None
            return datetime.time(v_.hour, v_.minute, v_.second)
        return None

    @classmethod
    def new(cls, value):
        if value is None:
            return AttributeValueNull()
        if isinstance(value, (datetime.datetime, datetime.time)):
            return cls(value.hour, value.minute, value.second)
        elif isinstance(value, str):
            try:
                v_ = str2time(value)
            except ValueError:
                return AttributeValueNull()
            return cls(v_.hour, v_.minute, v_.second)
        return AttributeValueNull()


class AttributeValueDateTime(AttributeValueAbstract, datetime.datetime):
    basecls = datetime.datetime

    def base(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            return None
        elif isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return datetime.datetime(value.year, value.month, value.day, 0, 0, 0)
        elif isinstance(value, datetime.datetime):
            return datetime.datetime(value.year, value.month, value.day, value.hour, value.minute, value.second)
        elif isinstance(value, str):
            try:
                v_ = str2datetime(value)
            except ValueError:
                return None
            return datetime.datetime(v_.year, v_.month, v_.day, v_.hour, v_.minute, v_.second)
        return None

    @classmethod
    def new(cls, value):
        if value is None:
            return AttributeValueNull()
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return cls(value.year, value.month, value.day, 0, 0, 0)
        elif isinstance(value, datetime.datetime):
            return cls(value.year, value.month, value.day, value.hour, value.minute, value.second)
        elif isinstance(value, str):
            try:
                v_ = str2datetime(value)
            except ValueError:
                return AttributeValueNull()
            return cls(v_.year, v_.month, v_.day, v_.hour, v_.minute, v_.second)
        return AttributeValueNull()


class AttributeValueVirtual(AttributeValueAbstract):
    check_modified = False

    def __init__(self):
        super(AttributeValueVirtual, self).__init__()
        self.instance = None
        self.model_k = None
        self.c = None
        self._value = None
        self._loaded = False

    def get_value(self):
        if self._loaded is False:
            self._value = self.load()
        return self._value

    def set_value(self, instance, key, value):
        return value

    def load(self):
        pass

    def reload(self):
        self._value = self.load()
        return self._value

    def reset(self):
        self._loaded = False
        self._value = None

    def pretend_loaded(self):
        self._loaded = True

    @property
    def loaded(self):
        return self._loaded


class ValueArrayAbstract(AttributeValueVirtual):
    basecls = False
    check_modified = False

    def __init__(self):
        super(ValueArrayAbstract, self).__init__()
        self._original_values = None
        self._values = None
        self._objects = None
        self._to_delete = list()
        self.reset()

    def __repr__(self):
        return "Array"

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def _verify_changes(self):
        if self._original_values == self._values and self.model_k in self.instance.__changes__:
            del(self.instance.__changes__[self.model_k])
        elif self._original_values != self._values:
            self.instance.__changes__[self.model_k] = (self._original_values, self._values)

    def write(self):
        for obj in self._to_delete:
            obj.delete()
        if isinstance(self._objects, dict):
            for k in self._objects:
                obj = self._objects[k]
                obj.write(session=self.instance.__session__)
        else:
            for obj in self._objects:
                obj.write(session=self.instance.__session__)
        self._to_delete = list()

    def load(self):
        pass

    def ensure(self):
        if self._loaded:
            return
        self.load()

    def reload(self):
        self.reset()
        self.load()

    def reset(self):
        pass

    def get_value(self):
        self.ensure()
        return self

    def set_value(self, instance, key, value):
        pass

    def _assign_with_instance(self, obj):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of virtual related iterable until model been defined!")
        model = c.model
        if model is None:
            raise OrmNotDefinedYet("cannot access values of virtual related iterable until model been defined!")
        pk = model.__meta__.primary_key
        for k in pk:
            setattr(obj, "parent_%s" % k, getattr(self.instance, k))


