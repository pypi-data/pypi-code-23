import warnings
import re
from collections import OrderedDict
from functools import partial

CONFIGURATION_DEFAULTS = OrderedDict([
    ('gzip', None),

    ('root-directory', None),
    ('root-address', 'https://localhost'),

    ('fossil-route', 'scm'),
    ('fossil-repositories', '/home/protected/r'),
    ('fossil-executable', '/usr/bin/env fossil'),
    ('fossil-debug', None),

    ('redirects', None),
    ('extra-link-checks', None),
    ('404', '404.html'),

    ('output', 'output'),
])

class _ConfigWarning(Warning):
    pass

def _split(line):
    separator = re.compile(r'[=:]')
    if re.search(separator, line):
        rawkey, rawvalue = re.split(separator, line, 1)
    else:
        raise ValueError('Invalid line: %s' % line)
    return rawkey.strip(), rawvalue.strip()

def _generic(defaults, fp):
    c = dict(defaults)
    for line in fp:
        before_comment = line.split('#')[0].strip()
        if before_comment:
            key, value = _split(before_comment)
            if key in c:
                c[key] = value
            elif key.lower().startswith('x-'):
                pass
            else:
                warnings.warn('Skipping bad key: %s' % key, _ConfigWarning)
    return c

article_header = partial(_generic, {
    'title': None,
    'description': None,
    'date': None,

    'centered': None,
    'nobread': None,
})

configuration_file = partial(_generic, CONFIGURATION_DEFAULTS)
