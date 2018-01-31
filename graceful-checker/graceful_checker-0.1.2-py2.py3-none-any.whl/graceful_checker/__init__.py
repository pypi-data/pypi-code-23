#-*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import pkg_resources
import argparse
import json
import re
import time
from collections import defaultdict

import six

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'

# http://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
ansi_escape = re.compile(r'\x1b[^m]*m')


# TODO: Use a Builder or an options data object instead, since this has a lot of arguments.
def graceful_check(
        linter_name,
        grace_file,
        grace_decrease,
        get_errors,
        explanation=None,
        save=False,
        all=False,
        color=False,
        allowance=7
):
    """

    :param linter_name:
    :param grace_file: file storing the grace amounts per file
    :param grace_decrease: amount of grace decrease per day
    :param get_errors: provides a list of (error: string, is_crit: bool, filename: string)
    :param explanation: An explanation to print when printing the results
    :param save: whether to save the current counts as new grace counts
    :param all: show all errors
    :param color: leave color codes if possible
    :param allowance: grace allowance to add to the saved counts, if save is True. Otherwise does nothing.
    :return:
    """
    def _print(text='', *args, **kwargs):
        print("[%s] %s" % (linter_name, text), *args, **kwargs)

    try:
        with open(grace_file, 'r') as f:
            grace = json.load(f)
    except IOError:
        grace = {'time': time.time(), 'counts': {}}

    # slowly decrease grace -- 'grace_decrease' per day
    grace_delta = int((time.time() - grace['time'])/3600/24 * grace_decrease)
    total_grace = sum([v for v in six.itervalues(grace['counts'])])

    errors = []
    crit_errors = []
    file_errors = defaultdict(list)
    for error, is_crit, filename in get_errors():
        if not color:
            error = ansi_escape.sub('', error)
            filename = os.path.relpath(ansi_escape.sub('', filename), os.path.dirname(grace_file))

        errors.append(error)
        if is_crit:
            crit_errors.append(error)
        file_errors[filename].append(error)

    if save:
        # save the grace file
        # 1 week allowance, then grace will start decreasing
        keys = file_errors.keys()
        counts = {name: len(errors) for name, errors in six.iteritems(file_errors)}
        if counts:
            for k in keys:
                counts[k] += allowance
        with open(grace_file, 'w') as f:
            json.dump({
                'time': time.time(),
                'counts': counts
            }, f)

    grace_gap = len(errors) - max((total_grace - grace_delta), 0)
    _print('%d errors found. Grace remaining: %d' % (len(errors), -grace_gap))

    ok = True

    if explanation:
        _print(explanation)

    if grace_gap > 0:
        _print()
        _print('ERROR: Total number of errors has exceeded the adjusted grace count. Please reduce the number of errors by %d' % grace_gap)
        _print('Here are some suggestions:')
        for error in errors[:grace_gap + 10]:
            _print(error)
        ok = False

    for file_name, curr_errors in six.iteritems(file_errors):
        gap = len(curr_errors) - grace['counts'].get(file_name, 0)
        if gap > 0:
            _print()
            _print('ERROR: grace exceeded for file %s. Please reduce it by at least %d.' % (file_name, gap))
            _print('Here are some suggestions:')
            for error in curr_errors[:gap + 10]:
                _print(error)
            ok = False

    if crit_errors:
        _print()
        _print('ERROR: %d (> 0) critical errors have been found:' % len(crit_errors))
        for error in crit_errors:
            _print(error)
        ok = False

    if all:
        _print()
        _print('All errors requested to be printed. Printing...')
        for error in errors:
            _print(error)

    return ok


def parse_graceful_checker_options(description, grace_file=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--save', dest='save', action='store_true', help='Store the current counts as the new grace counts')
    parser.add_argument('--grace-file', dest='grace_file', type=six.text_type, default=grace_file, help='Path of the grace counts file')
    parser.add_argument('--all', dest='all', action='store_true', help='Show all errors')
    parser.add_argument('--color', dest='color', action='store_true', help='Leave color codes (if possible)')
    parser.add_argument('--allowance', dest='allowance', action='store', default=7, help='Grace allowance', type=int)
    return parser.parse_known_args()[0]
