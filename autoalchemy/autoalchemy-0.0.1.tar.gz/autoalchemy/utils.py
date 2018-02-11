"""Utilities for navigating the directory structure."""

import json
import os
import time
from timeit import default_timer

import numpy as np
import pandas as pd

# TODO: Verbose printing class here


def make_valid_name(string):
    """Remove illegal symbols from a string."""
    invalid_symbols = [' ', '.', '\\', '/', '$', '-', '=', '%', ';', ':', '&']
    for sym in invalid_symbols:
        string = string.replace(sym, '_')
    if string[0] in list('0123456789'):
        string = 'STRING_' + string

    python_reserved_words = set([
        'False', 'class', 'finally', 'is', 'return',
        'None', 'continue', 'for', 'lambda', 'try',
        'True', 'def', 'from', 'nonlocal', 'while',
        'and', 'del', 'global', 'not', 'with',
        'as', 'elif', 'if', 'or', 'yield',
        'assert', 'else', 'import', 'pass',
        'break', 'except', 'in', 'raise',
    ])
    if string in python_reserved_words:
        string = 'RESERVED_' + string

    return string


def is_valid_name(string):
    return string == make_valid_name(string)


def listdir_full(directory):
    """Return the full paths of all files in the directory."""
    if not os.path.isdir(directory) and os.path.isabs(directory):
        raise ValueError('Arg must be a full absolute directory path')
    return [os.path.join(directory, file) for file in os.listdir(directory)]


def get_missing_files(files, directory):
    """Given a list of files and a directory, return the list of missing files."""
    full_paths = listdir_full(directory)
    missing_files = []
    for file in files:
        if not any([fp.endswith(file) for fp in full_paths]):
            missing_files.append(file)
    return missing_files


def sanitize_path_args(func):
    # os.path.join causes problems if an argument is in directory form
    def decorator(*args):
        args = list(args)
        for i in range(len(args)):
            args[i] = args[i].lstrip('/').lstrip('\\')
        args = tuple(args)
        return func(*args)
    return decorator


def parse_config(config_path):
    """Load the database config from JSON."""
    if not os.path.exists(config_path):
        raise ValueError('Config must be placed at {0}'.format(config_path))

    with open(config_path, 'r') as fp:
        config = json.load(fp)

    required_fields = ['host', 'user', 'password', 'db']
    for field in required_fields:
        if not field in config:
            raise ValueError('Required field {0} not found in config.'.format(field))

    return config


def get_filename(file):
    """Given a path, get the file's name without parent path and extension."""
    _, file = os.path.split(file)
    file, _ = os.path.splitext(file)
    return file


def print_highlighted(msg):
    hl = len(msg) * '*'
    highlighted = '\n{hl}\n{msg}\n{hl}\n'.format(hl=hl, msg=msg)
    print(highlighted)


def time_function(func):
    """Decorator that adds execution time printing to a function."""
    def decorator(*args, **kwargs):
        t0 = default_timer()
        res = func(*args, **kwargs)
        t1 = default_timer()
        elapsed = round(t1 - t0, 2)
        print('Time elapsed: {0} seconds.'.format(elapsed))
        return res
    return decorator


def remove_numeric_head(string):
    # TODO: use regex here the while loop is awful
    remove_chars = list('0123456789_')
    if all([s in remove_chars for s in string]):
        return 'STRING_' + string
    else:
        i = 0
        while string[i] in remove_chars:
            i += 1
        return string[i:]


def validate_path(file_path):
    if not isinstance(file_path, str):
        raise ValueError('file_path should be a string.')
    if not os.path.exists(file_path):
        raise ValueError('No file found at {0}'.format(file_path))
    if not (file_path.endswith('.txt') or file_path.endswith('.csv')):
        raise ValueError('file_path should point to a csv or tsv.')
    return file_path
