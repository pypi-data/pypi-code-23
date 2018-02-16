# coding=utf-8

import elib


def test_pretty():
    obj = {
        'test': 'value',
        'nested': {
            'test': 'value'
        },
        'a': 't',
        'b': 't',
        'c': 't',
        'd': 't',
        'e': 't',
        'f': 't',
        'g': 't',
        'h': 't',
        'i': 't',
        'j': 't',
        'k': 't',
        'l': 't',
    }
    out = elib.pretty_format(obj)
    print(out)
    assert out == """    {'a': 't',
     'b': 't',
     'c': 't',
     'd': 't',
     'e': 't',
     'f': 't',
     'g': 't',
     'h': 't',
     'i': 't',
     'j': 't',
     'k': 't',
     'l': 't',
     'nested': {'test': 'value'},
     'test': 'value'}"""


def test_pretty_no_indent():
    obj = {
        'test': 'value'
    }
    out = elib.pretty_format(obj, indent=0)
    assert out == "{'test': 'value'}"
