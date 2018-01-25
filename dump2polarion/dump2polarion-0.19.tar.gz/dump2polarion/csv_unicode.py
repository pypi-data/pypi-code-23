# -*- coding: utf-8 -*-

import csv
import codecs


def get_csv_reader(f, dialect=csv.excel, encoding='utf-8', **kwds):
    try:
        # pylint: disable=pointless-statement
        unicode
        return UnicodeReader(f, dialect=dialect, encoding=encoding, **kwds)
    except NameError:
        return csv.reader(f, dialect=dialect, **kwds)


class UTF8Recoder(object):
    """Iterator that reads an encoded stream and reencodes the input to UTF-8."""
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeReader(object):
    """ A CSV reader which will iterate over lines in the CSV file that
    is encoded in the given encoding."""
    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, 'utf-8') for s in row]

    def __iter__(self):
        return self
