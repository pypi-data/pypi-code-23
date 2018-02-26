from datetime import timedelta
import re


RE_AGE = re.compile(r'^(?P<age>\d+)(?P<unit>[smhdwMy])$')
UNITS = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800,    # 7 days
    'M': 2592000,   # 30 days
    'y': 31536000,  # 365 days
}


def parse(age):
    """Parse a file age.

    >>> parse('42s')
    datetime.timedelta(0, 42)
    >>> parse('2m')
    datetime.timedelta(0, 120)
    >>> parse('10h')
    datetime.timedelta(0, 36000)
    >>> parse('1d')
    datetime.timedelta(1)
    >>> parse('2w')
    datetime.timedelta(14)
    >>> parse('3M')
    datetime.timedelta(90)
    >>> parse('1y')
    datetime.timedelta(365)

    """
    match = RE_AGE.match(age)

    if match is None:
        raise ValueError('Invalid age: %r' % age)

    data = match.groupdict()

    return timedelta(seconds=int(data['age']) * UNITS[data['unit']])
