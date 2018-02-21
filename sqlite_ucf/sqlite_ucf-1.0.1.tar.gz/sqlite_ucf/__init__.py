# -*- coding: utf-8 -*-

from sqlite3 import *
import re
from functools import lru_cache

_sqlite3_connect = connect
unicode_case_folding_default = False


def _uni_collate(str1, str2):
    str1 = str1.upper()
    str2 = str2.upper()
    if str1 > str2:
        return 1
    elif str1 < str2:
        return -1
    else:
        return 0


@lru_cache()
def _like_pattern_to_re_pattern(pattern, escape):
    pat = []
    escaped = False
    for char in pattern:
        if escaped:
            pat.append(re.escape(char))
            escaped = False
            continue
        if char == escape:
            escaped = True
        elif char == '_':
            pat.append('.')
        elif char == '%':
            pat.append('.*')
        else:
            pat.append(re.escape(char))
    return ''.join(pat)


def _uni_like_escape(pattern, string, escape):
    re_pattern = _like_pattern_to_re_pattern(pattern, escape)
    try:
        return bool(re.match(re_pattern + '$', string, re.IGNORECASE | re.UNICODE))
    except Exception:
        return False


def _uni_like(pattern, string):
    return _uni_like_escape(pattern, string, None)


def connect(database, unicode_case_folding=None, **kwargs):
    """
    connect(database[, ascii_case_folding, timeout, detect_types, isolation_level,
            check_same_thread, factory, cached_statements, uri])

    Opens a connection to the SQLite database file *database*. You can use
    ":memory:" to open a database connection to a database that resides in
    RAM instead of on disk.
    If ascii_ascii_case_folding is not specified it defaults to the value of the module
    level variable *ascii_case_folding_default*
    """
    if unicode_case_folding is None:
        unicode_case_folding = unicode_case_folding_default
    connection = _sqlite3_connect(database, **kwargs)
    if unicode_case_folding:
        # replace builtin collation with case-insensitive unicode-aware versions
        connection.create_collation('NOCASE', _uni_collate)
        # replace builtin functions with case-insensitive unicode-aware versions
        connection.create_function('LOWER', 1, lambda x: x.lower())
        connection.create_function('UPPER', 1, lambda x: x.upper())
        connection.create_function('LIKE', 2, _uni_like)
        connection.create_function('LIKE', 3, _uni_like_escape)
        connection.execute('REINDEX NOCASE')
    return connection
