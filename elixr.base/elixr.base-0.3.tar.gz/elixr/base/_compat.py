import sys


PY3 = sys.version_info.major > 2


if PY3:
    text_type = str
    range_type = range
    string_types = (str,)
    integer_types = (int,)

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())
else:
    text_type = unicode
    range_type = xrange
    integer_types = (int, long)
    string_types = (str, unicode)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()
