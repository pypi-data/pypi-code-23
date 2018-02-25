# coding=utf-8
"""
Formats an object for representation on the console or in a log
"""


import pprint


def _indent(text, indent=4):
    fstring = ' ' * indent + '{}'
    return ''.join([fstring.format(l) for l in text.splitlines(True)])


def pretty_format(obj, indent=4):
    """
    Formats an object for representation on the console or in a log

    Args:
        obj: object to represent
        indent: indent (defaults to 4)

    Returns: formatted text

    """
    return _indent(pprint.pformat(obj, width=120), indent=indent)
