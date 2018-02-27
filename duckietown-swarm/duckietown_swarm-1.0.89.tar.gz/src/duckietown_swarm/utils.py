from contextlib import contextmanager
import math
import os
from tempfile import NamedTemporaryFile
import time

import base58
from contracts.utils import indent, check_isinstance
from decorator import decorator
from system_cmd.meat import system_cmd_result


def get_sha256_base58(contents):
    import hashlib
    m = hashlib.sha256()
    m.update(contents)
    s = m.digest()
    return base58.b58encode(s)


def get_sha256_for_file_hex(filename):
    import hashlib
    m = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            m.update(chunk)
    return m.hexdigest()


def yaml_dump_omaps(s):
    from ruamel import yaml
    res = yaml.dump(s, Dumper=yaml.RoundTripDumper, allow_unicode=False)
    return res


def yaml_load_omaps(s):
    from ruamel import yaml
    res = yaml.load(s, Loader=yaml.UnsafeLoader)
    return res


@contextmanager
def tmpfile(suffix):
    ''' Yields the name of a temporary file '''
    temp_file = NamedTemporaryFile(suffix=suffix)
    try:
        yield temp_file.name
    finally:
        temp_file.close()

# -*- coding: utf-8 -*-


__all__ = [
    'memoize_simple',
]


def memoize_simple(obj):
    cache = obj.cache = {}

    def memoizer(f, *args):
        key = (args)
        if key not in cache:
            cache[key] = f(*args)
        assert key in cache

        try:
            cached = cache[key]
            return cached
        except ImportError:  # pragma: no cover  # impossible to test
            del cache[key]
            cache[key] = f(*args)
            return cache[key]

            # print('memoize: %s %d storage' % (obj, len(cache)))

    return decorator(memoizer, obj)


def pretty_print_dictionary(d):
    lengths = [len(k) for k in d.keys()]
    if not lengths:
        return 'Empty.'

    s = ""
    for k, v in d.items():
        if isinstance(k, tuple):
            k = k.__repr__()
        if s:
            s += '\n\n'
        s += k
        s += '\n\n' + indent(str(v), '  ')
    return s


def get_all_available(queue):
    ''' Gets all that are available currently. '''
    from Queue import Empty
    res = []
    while True:
        try:
            x = queue.get(block=False)
            res.append(x)
        except Empty:
            break
    return res


def get_at_least_one(queue, timeout):
    """ This waits for one, and then waits at most timeout. """
    from Queue import Empty
    s = []
    t0 = time.time()
    while True:
        try:
            block = len(s) == 0
            x = queue.get(block=block, timeout=timeout)
            s.append(x)

            if time.time() < t0 + timeout:
                wait = t0 + timeout - time.time()
                time.sleep(wait)
        except Empty:
            break

    T = time.time() - t0
    if False:
        print('Got %s objects after %.1f s (timeout %.1f s)' % (len(s), T, timeout))
    return s


def friendly_time_since(t0):
    if t0 == 0:
        return 'never'
    delta = time.time() - t0
    return duration_compact(delta)


def duration_compact(seconds):
    if seconds < 0:
        raise ValueError(seconds)
    seconds = int(math.ceil(seconds))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365.242199)

    minutes = int(minutes)
    hours = int(hours)
    days = int(days)
    years = int(years)

    duration = []
    if years > 0:
        duration.append('%dy' % years)
    else:
        if days > 0:
            duration.append('%dd' % days)
        if (days < 3) and (years == 0):
            if hours > 0:
                duration.append('%dh' % hours)
            if (hours < 3) and (days == 0):
                if minutes > 0:
                    duration.append('%dm' % minutes)
                if (minutes < 3) and (hours == 0):
                    if seconds > 0:
                        duration.append('%ds' % seconds)

    return ' '.join(duration)


class DoAtInterval():

    def __init__(self, every_s, after="0s"):
        self.last = 0
        self.every = as_seconds(every_s)
        self.after = as_seconds(after)
        self.first = time.time()
        self.is_first_time = True

    def its_time(self):

        delta = time.time() - self.first

        do = (delta > self.after) and (self.is_first_time or  (delta > self.last))

        self.is_first_time = False

        if do:
            self.last = time.time()
            return True
        else:
            return False


def as_seconds(s):
    ''' Converts expressions such as 10m, 2h, 3d into number of seconds '''
    if isinstance(s, (float, int)): return s
    check_isinstance(s, str)
    units = s[-1]
    mult = {'s':1,
            'm':60,
            'h':60 * 60,
            'd':60 * 60 * 24,
            'w':60 * 60 * 24 * 7 }[units]
    n = float(s[:-1])
    return n * mult


class MakeLines():

    def __init__(self):
        self.data = ''
        self.lines_in = []

    def get_lines(self):
        for l in self.lines_in:
            yield l
        self.lines_in = []

    def push(self, ks):
        for k in ks:
            if k == '\n':
                self.lines_in.append(self.data)
                self.data = ''
            else:
                self.data += k


class LineSplitter(object):
    """ A simple utility to split an incoming sequence of chars
        in lines. Push characters using append_chars() and
        get the completed lines using lines(). """

    def __init__(self):
        self.current = ''
        self.current_lines = []

    def append_chars(self, s):
        # TODO: make this faster
        s = str(s)
        for char in s:
            if char == '\n':
                self.current_lines.append(self.current)
                self.current = ''
            else:
                self.current += char

    def lines(self):
        """ Returns a list of line; empties the buffer """
        l = list(self.current_lines)
        self.current_lines = []
        return l


def now_until(delta):
    t = time.time()
    return [t, t + delta]


def download_url_to_file(url, filename):
    print('Download from %s' % (url))
    tmp = filename + '.tmp_download_file'
    cmd = [
        'wget',
        '-O',
        tmp,
        url
    ]
    d = os.path.dirname(tmp)
    if not os.path.exists(d):
        os.makedirs(d)
    res = system_cmd_result(cwd='.',
                          cmd=cmd,
                          display_stdout=True,
                          display_stderr=True,
                          raise_on_error=True,
                          write_stdin='',
                          capture_keyboard_interrupt=False,
                          env=None)

    if not os.path.exists(tmp) and not os.path.exists(filename):
        msg = 'Downloaded file does not exist but wget did not give any error.'
        msg += '\n url: %s' % url
        msg += '\n downloaded to: %s' % tmp
        msg += '\n' + indent(str(res), ' | ')
        d = os.path.dirname(tmp)
        r = system_cmd_result(d, ['ls', '-l'], display_stdout=False,
                          display_stderr=False,
                          raise_on_error=True)
        msg += '\n Contents of the directory:'
        msg += '\n' + indent(str(r.stdout), ' | ')
        raise Exception(msg)

    if not os.path.exists(filename):
        os.rename(tmp, filename)

#    logger.info('-> %s' % friendly_path(filename))
