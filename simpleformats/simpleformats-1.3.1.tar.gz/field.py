from __future__ import print_function, unicode_literals
"""
Fields define one value within a record, and can be one of the following types:
integer, decimal, date, string or constant.
"""
import ctxlogger
import re
import time
import unicodedata

from datetime import datetime
from decimal import Decimal, InvalidOperation
from six import text_type

from . import ParseException

## regular expressions for validating types of strings
## Can use these as constants to pass to parse_string

# basic, errs on the side of being too lenient
# don't want to reject valid addresses
EMAIL_STRING = r'^\S+@\S+\.\S+$'

# web addresses
URL_STRING = r'^[a-zA-Z]+://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(:[0-9]+)?[\./a-zA-Z0-9-]*(\?[a-zA-Z0-9%-]+(=[a-zA-Z0-9%-]+)?(&[a-zA-Z0-9%-]+(=[a-zA-Z0-9%-]+)?)*)?$'

## Happy to take suggestions for other "standard" string types


def parse_int(field, required=True, nonzero=False, positive=False, **kwargs):
    """
    Extract an integer from raw field data

    field - the raw data to parse
    required - throw exception if missing or blank
    nonzero - throw exception if zero
    positive - throw exception if below zero
    """
    try:
        value = int(field)
    except (ValueError, TypeError) as e:
        if not required:
            return None
        ctxlogger.exception(ParseException,
            'Value "{}" is not an integer'.format(field), orig_exc=e)

    if nonzero and value == 0:
        ctxlogger.exception(ParseException, 'Value is zero')
    if positive and value < 0:
        ctxlogger.exception(ParseException, 'Value is negative')

    return value

def unparse_int(value, length=None, filler='0', **kwargs):
    """
    Convert an integer into raw field data

    value - the integer to convert
    length - the length of the resulting field (or None if irrelevant)
    filler - the fill character to use to pad to length (default 0)
    """
    parse_int(value, **kwargs) # re-use existing validation
    return unparse_string(value, length, filler=filler, **kwargs)


def parse_decimal(field, required=True, strict=True, min_precision=None,
                  max_precision=None, **kwargs):
    """
    Extract a decimal from raw field data

    field - the raw data to parse
    required - throw exception if missing or empty (default True)
    strict - don't strip invalid characters (default True)
    min_precision - the smallest acceptable precision (None for any)
    max_precision - the maximum acceptable precision (None for any)
    precision - the precision the field should have (None for any)
    """
    if not min_precision and not max_precision:
        try: # in case we're using the same format spec for in and out
            min_precision = kwargs['precision']
            max_precision = kwargs['precision']
        except KeyError:
            pass

    val = parse_string(field, required=required, **kwargs)
    if val == None:
        return None

    if not strict:
        val = re.sub('[^0-9+.-]+', '', val)

    try:
        val = Decimal(val)
        exp = -(val.as_tuple()[2])
    except (TypeError, InvalidOperation) as e:
        if not required:
            return None
        ctxlogger.exception(ParseException,
            'Could not parse "{}" as a decimal'.format(field), orig_exc=e)

    if min_precision != None and min_precision > exp:
        ctxlogger.exception(ParseException,
            'Minimum precision not met: {} < {}'.format(exp, min_precision))
    if max_precision != None and max_precision < exp:
        ctxlogger.exception(ParseException,
            'Maximum precision exceeded: {} > {}'.format(exp, max_precision))
    return val

def unparse_decimal(value, length=None, precision=None, filler='0', **kwargs):
    """
    Convert a decimal into raw field data

    value - the value to convert
    length - the length of the resultant field (None if irrelevant)
    precision - how many digits to round to or None (default) to not round
    filler - the character the field is padded with if too short (default 0)
    """
    decvalue = parse_decimal(value)
    try:
        decvalue = round(decvalue, precision)
    except TypeError: # precision is None, no rounding required
        pass
    return unparse_string(decvalue, length=length, filler=filler, **kwargs)


def parse_boolean(field, positive='1', negative='0', ignore_case=True,
                  required=True, **kwargs ):
    """
    Extract a boolean value from raw field data

    field - the raw data
    positive - the value for true fields
    negative - the value for false fields
    ignore_case - case-insensitive matching (default True)
    required - throw exception if missing or empty (default True)
    """
    value = parse_string(field, strip_spaces=True, required=required, **kwargs)
    if ignore_case:
        value = value.lower()
        positive = positive.lower()
        negative = negative.lower()

    if positive == value:
        return True
    if negative == value:
        return False
    if required:
        ctxlogger.exception(ParseException,
                            'Incorrect string for required value')
    return False

def unparse_boolean(value, positive = '1', negative = '0', **kwargs):
    """
    Convert a boolean value into raw field data

    value - the boolean to convert
    positive - the string to use for True values
    negative - the string to use for False values
    """
    if value:
        field = positive
    else:
        field = negative
    return unparse_string(field, **kwargs)


def parse_string(field, length=None, required=True, strip_spaces=True,
                        match=None, **kwargs):
    """
    Extract a string from raw field data

    field - the raw data
    length - the maximum length of the string
    required - exception if missing or blank
    strip_spaces - remove whitespace from returned value
    match - a regex to match the string value against
    """

    value = None
    if field != None:
        value = text_type(field)
        if strip_spaces:
            value = value.strip()

    if required and not value:
        ctxlogger.exception(ParseException, 'Empty string for required value')
    if match and not re.match(match, value):
        ctxlogger.exception(ParseException, 'Does not match regex')
    if length != None and len(value) > length:
        if required:
            ctxlogger.exception(ParseException, 'String value too long')
        else:
            value = value[:length]

    if value is not None:
        return unicodedata.normalize('NFKD', value)
    else:
        return value

def unparse_string(value, length=None, justify='right', filler=' ', match=None,
                   **kwargs):
    """
    Convert a string into raw field data

    value - the string to convert
    length - the length of the resulting data (None if it doesn't matter)
    justify - how to justify the string if it's shorter than length
    filler - the character to use to fill if it's shorter than length
    match - a regex the string must match to be valid
    """

    strval = parse_string(value, match = match)

    if length == None:
        return strval

    # if we have a length, we need to justify the string within that length
    strlen = len(strval)

    if justify == 'left':
        op = '<'
    elif justify == 'center':
        op = '^'
    elif justify == 'right':
        op = '>'
    else:
        ctxlogger.exception(ParseException,
                            'Invalid justification "{}"'.format(justify))

    fmt = '{0:%s%s%d.%d}' % (filler, op, length, length)
    try:
        return fmt.format(strval)
    except ValueError as e:
        ctxlogger.exception(ParseException,
            'Invalid fill character "{}"'.format(filler), orig_exc = e)


def parse_date(field, fmt, required=True, **kwargs):
    """
    Extract a datetime object from raw field data

    field - the raw data to parse
    fmt - the expected datetime format
    required - throw exception if missing or blank
    """
    value = parse_string(field, required=required, **kwargs)
    try:
        return datetime(*time.strptime(value, fmt)[:6])
    except Exception as e:
        if required:
            ctxlogger.exception(ParseException, str(e), orig_exc=e)
    return None

def unparse_date(value, length=None, fmt='%c', **kwargs):
    """
    Convert a datetime object into raw field data

    value - the datetime object to convert
    length - the required length of the resulting field
    fmt - the output format for the datetime
    """
    try:
        field = value.strftime(fmt)
    except Exception as e:
        ctxlogger.exception(ParseException, str(e), orig_exc=e)
    return unparse_string(field, length, **kwargs)


def parse_constant(field, constant, ignore_case=False, **kwargs):
    """
    Validate a constant value

    field - the raw field value to parse
    constant - the constant value it should equal
    required - throw exception if missing or blank
    """
    value = parse_string(field, **kwargs)

    if ignore_case:
        value = value.lower()
        constant = constant.lower()

    if constant != value:
        ctxlogger.exception(ParseException,
            '{} does not equal {}'.format(value, constant))

    return constant

def unparse_constant(value, length, constant, **kwargs):
    """
    Return the constant value

    value - ignored, but needed for consistency with other unparse functions
    length - the length of resulting field
    constant - the constant value to use
    """
    return unparse_string(constant, length=length, **kwargs)


def parse_enum(field, options, ignore_case=False, **kwargs):
    """
    Validate against a set of values 

    field - the raw field value to parse
    options - iterable list of values to match against
    required - throw exception if missing or blank
    """
    value = parse_string(field, **kwargs)

    if ignore_case:
        value = value.lower()
        options = [o.lower() for o in options]

    if value in options:
        return value

    ctxlogger.exception(ParseException, '{} is not in {}'.format(
                                                        value, tuple(options)))

def unparse_enum(value, length, options, **kwargs):
    """
    Return the constant value

    value - the value of the field
    length - the length of resulting field
    options - iterable of valid values
    """
    field = parse_enum(value, options, length=length, **kwargs)
    return unparse_string(field, length=length, **kwargs)


## The field class wraps the above conversion functions,
## storing the details about a specific field in a record,
## such as the start and end points (for a fixed width field),
## or whether the field is required.

class field(object):
    def __init__(self, start=None, end=None, length=None, **kwargs):
        self.start = start
        self.end = end
        self.flags = kwargs
        if start != None and end != None:
            length = end - start
        self.flags['length'] = length

    def get_field(self, record):
        if self.end:
            if self.end > len(record):
                if self.flags.get('required', True):
                    ctxlogger.exception(ParseException,
                        'Record too short ({} < {})'.format(
                                                        len(record), self.end))
                return None
            return record[self.start:self.end]
        return record[self.start:]

    def parse(self, record):
        field = record
        # If we have a start set, then the field is a substring of the whole
        # record, so pull that out first
        if self.start != None:
            field = self.get_field(record)
        return self._parse(field, **self.flags)

    def unparse( self, value ):
        return self._unparse(value, **self.flags)

class int_field( field ):
    def _parse(self, *args, **kwargs):
        return parse_int(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_int(*args, **kwargs)

class decimal_field( field ):
    def _parse(self, *args, **kwargs):
        return parse_decimal(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_decimal(*args, **kwargs)

class boolean_field(field):
    def _parse(self, *args, **kwargs):
        return parse_boolean(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_boolean(*args, **kwargs)

class string_field(field):
    def _parse(self, *args, **kwargs):
        return parse_string(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_string(*args, **kwargs)

class date_field(field):
    def _parse(self, *args, **kwargs):
        return parse_date(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_date(*args, **kwargs)

class constant_field(field):
    def _parse(self, *args, **kwargs):
        return parse_constant(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_constant(*args, **kwargs)

class enum_field(field):
    def _parse(self, *args, **kwargs):
        return parse_enum(*args, **kwargs)

    def _unparse(self, *args, **kwargs):
        return unparse_enum(*args, **kwargs)
