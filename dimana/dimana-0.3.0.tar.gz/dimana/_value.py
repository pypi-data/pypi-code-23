import re
from functools import wraps
from decimal import Decimal, InvalidOperation
from dimana.exceptions import ValueParseError
from dimana._typecheck import typecheck
from dimana._units import Units, Scalar


# Private Units-matching decorator:
def units_must_match(method):

    @wraps(method)
    def m(self, other):
        typecheck(other, Value)
        self.units.match(other.units)
        return method(self, other)
    return m


class Value (object):
    def __init__(self, spec, units=None):
        if units is None:
            (spec, units) = _parse_value(spec)

        typecheck(spec, Decimal)
        typecheck(units, Units)

        self.amount = spec
        self.units = units

    # str/repr Methods:
    def __str__(self):
        if self.units is Scalar:
            return str(self.amount)
        else:
            return '{} [{}]'.format(self.amount, self.units)

    def __repr__(self):
        return '<{} {!r}>'.format(type(self).__name__, str(self))

    # Ordering Methods:
    @units_must_match
    def __lt__(self, other):
        return self.amount < other.amount

    @units_must_match
    def __le__(self, other):
        return self.amount <= other.amount

    @units_must_match
    def __eq__(self, other):
        return self.amount == other.amount

    @units_must_match
    def __ne__(self, other):
        return self.amount != other.amount

    @units_must_match
    def __gt__(self, other):
        return self.amount > other.amount

    @units_must_match
    def __ge__(self, other):
        return self.amount >= other.amount

    # Arithmetic Methods:
    def __pos__(self):
        return self

    def __neg__(self):
        return Value(-self.amount, self.units)

    @units_must_match
    def __add__(self, other):
        return Value(self.amount + other.amount, self.units)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        typecheck(other, Value)
        return Value(self.amount * other.amount, self.units * other.units)

    def __div__(self, other):
        typecheck(other, Value)
        return Value(self.amount / other.amount, self.units / other.units)

    __truediv__ = __div__

    def __pow__(self, other, modulus=None):
        if modulus is None:
            return Value(self.amount ** other, self.units ** other)
        else:
            raise TypeError('Modulus not supported for {!r}', self)


# UGLY HACK: work-around circular import issue:
Units._Value = Value


# Private
def _parse_value(text):
    m = _rgx.match(text)
    if m is None:
        raise ValueParseError('Could not parse Value: {!r}', text)

    dectext = m.group('decimal')
    try:
        decimal = Decimal(dectext)
    except InvalidOperation as e:
        raise ValueParseError(
            'Could not parse decimal {!r} of Value: {}',
            dectext,
            e,
        )

    unitext = m.group('units')
    if unitext is None:
        units = Scalar
    else:
        units = Units(unitext)
    return (decimal, units)


_rgx = re.compile(r'^(?P<decimal>\S+)( +\[(?P<units>.*?)\])?$')
