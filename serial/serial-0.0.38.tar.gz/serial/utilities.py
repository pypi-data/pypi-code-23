# region Backwards Compatibility
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, \
    with_statement

from future import standard_library

standard_library.install_aliases()
from builtins import *
# endregion

from io import UnsupportedOperation

from serial import errors

import builtins

from collections import Callable, OrderedDict
from unicodedata import normalize

import re
import inspect
from keyword import iskeyword

try:
    import typing
except ImportError:
    typing = None

try:
    from inspect import signature
    getargspec = None
except ImportError:
    signature = None
    try:
        from inspect import getfullargspec
    except ImportError:
        from inspect import getargspec as getfullargspec


def qualified_name(t):
    # type: (type) -> str
    """
    >>> print(qualified_name(qualified_name))
    qualified_name

    >>> from serial import model
    >>> print(qualified_name(model.marshal))
    serial.model.marshal
    """
    if hasattr(t, '__qualname__'):
        tn = t.__qualname__
    else:
        tn = t.__name__
    if t.__module__ not in ('builtins', '__builtin__', '__main__', __name__):
        tn = t.__module__ + '.' + tn
    return tn


def property_name(string):
    # type: (str) -> str
    """
    Converts a "camelCased" attribute/property name, or a name which conflicts with a python keyword, to a
    pep8-compliant property name.

    >>> print(property_name('theBirdsAndTheBees'))
    the_birds_and_the_bees

    >>> print(property_name('FYIThisIsAnAcronym'))
    fyi_this_is_an_acronym

    >>> print(property_name('in'))
    in_

    >>> print(property_name('id'))
    id_
    """
    pn = re.sub(
        r'__+',
        '_',
        re.sub(
            r'[^\w]+',
            '',
            re.sub(
                r'([a-zA-Z])([0-9])',
                r'\1_\2',
                re.sub(
                    r'([0-9])([a-zA-Z])',
                    r'\1_\2',
                    re.sub(
                        r'([A-Z])([A-Z])([a-z])',
                        r'\1_\2\3',
                        re.sub(
                            r'([a-z])([A-Z])',
                            r'\1_\2',
                            re.sub(
                                r'([^\x20-\x7F]|\s)+',
                                '_',
                                normalize('NFKD', string)
                            )
                        )
                    )
                )
            )
        )
    ).lower()
    if iskeyword(pn) or (pn in dir(builtins)):
        pn += '_'
    return pn


def class_name(string):
    """
    >>> print(class_name('the birds and the bees'))
    TheBirdsAndTheBees

    >>> print(class_name('the-birds-and-the-bees'))
    TheBirdsAndTheBees

    >>> print(class_name('**the - birds - and - the - bees**'))
    TheBirdsAndTheBees

    >>> print(class_name('FYI is an acronym'))
    FYIIsAnAcronym

    >>> print(class_name('in-you-go'))
    InYouGo

    >>> print(class_name('False'))
    False_

    >>> print(class_name('True'))
    True_

    >>> print(class_name('ABC Acronym'))
    ABCAcronym
    """
    return camel(string, capitalize=True)


def camel(string, capitalize=False):
    # type: (str, bool) -> str
    """
    >>> print(camel('the birds and the bees'))
    theBirdsAndTheBees

    >>> print(camel('the-birds-and-the-bees'))
    theBirdsAndTheBees

    >>> print(camel('**the - birds - and - the - bees**'))
    theBirdsAndTheBees

    >>> print(camel('FYI is an acronym'))
    fyiIsAnAcronym

    >>> print(camel('in-you-go'))
    inYouGo

    >>> print(camel('False'))
    false

    >>> print(camel('True'))
    true

    >>> print(camel('in'))
    in_
    """
    string = normalize('NFKD', string)
    characters = []
    if not capitalize:
        string = string.lower()
    capitalize_next = capitalize
    for s in string:
        if s in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
            if capitalize_next:
                if capitalize or characters:
                    s = s.upper()
            characters.append(s)
            capitalize_next = False
        else:
            capitalize_next = True
    cn = ''.join(characters)
    if iskeyword(cn) or (cn in dir(builtins)):
        cn += '_'
    return cn


def get_source(o):
    # type: (object) -> str
    if hasattr(o, '_source') and isinstance(o._source, str):
        result = o._source
    else:
        result = inspect.getsource(o)
    return result


def camel_split(string):
    # test: (str) -> str
    """
    >>> print('(%s)' % ', '.join("'%s'" % s for s in camel_split('theBirdsAndTheBees')))
    ('the', 'Birds', 'And', 'The', 'Bees')
    >>> print('(%s)' % ', '.join("'%s'" % s for s in camel_split('theBirdsAndTheBees123')))
    ('the', 'Birds', 'And', 'The', 'Bees', '123')
    >>> print('(%s)' % ', '.join("'%s'" % s for s in camel_split('theBirdsAndTheBeesABC123')))
    ('the', 'Birds', 'And', 'The', 'Bees', 'ABC', '123')
    >>> print('(%s)' % ', '.join("'%s'" % s for s in camel_split('the-Birds-And-The-Bees-ABC--123')))
    ('the', '-', 'Birds', '-', 'And', '-', 'The', '-', 'Bees', '-', 'ABC', '--', '123')
    >>> print('(%s)' % ', '.join("'%s'" % s for s in camel_split('THEBirdsAndTheBees')))
    ('THE', 'Birds', 'And', 'The', 'Bees')
    """
    words = []
    character_type = None
    acronym = False
    for s in string:
        if s in '0123456789':
            if character_type == 0:
                words[-1].append(s)
            else:
                words.append([s])
            character_type = 0
            acronym = False
        elif s in 'abcdefghijklmnopqrstuvwxyz':
            if character_type == 1:
                words[-1].append(s)
            elif character_type == 2:
                if acronym:
                    words.append([words[-1].pop()] + [s])
                else:
                    words[-1].append(s)
            else:
                words.append([s])
            character_type = 1
            acronym = False
        elif s in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if character_type == 2:
                words[-1].append(s)
                acronym = True
            else:
                words.append([s])
                acronym = False
            character_type = 2
        else:
            if character_type == 3:
                words[-1].append(s)
            else:
                words.append([s])
            character_type = 3
    return tuple(
        ''.join(w) for w in words
    )

def properties_values(o):
    # type: (object) -> typing.Iterable[typing.Tuple[str, Any]]
    for a in dir(o):
        if a[0] != '_':
            v = getattr(o, a)
            if not isinstance(v, Callable):
                yield a, v


EMPTY = None


class Empty(object):

    def __init__(self):
        if EMPTY is not None:
            raise errors.DefinitionExistsError(
                '%s may only be defined once.' % repr(self)
            )

    def __repr__(self):
        return (
            'EMPTY'
            if self.__module__ in ('__main__', 'builtins', '__builtin__', __name__) else
            '%s.EMPTY' % self.__module__
        )

    def __bool__(self):
        return False

    def __hash__(self):
        return 0


EMPTY = Empty()


def parameters_defaults(function):
    # type: (Callable) -> OrderedDict
    """
    Returns an ordered dictionary mapping a function's argument names to default values, or `EMPTY` in the case of
    positional arguments.

    >>> class x(object):
    ...
    ...    def __init__(self, a, b, c, d=1, e=2, f=3):
    ...        pass
    >>> print(list(parameters_defaults(x.__init__).items()))
    [('self', EMPTY), ('a', EMPTY), ('b', EMPTY), ('c', EMPTY), ('d', 1), ('e', 2), ('f', 3)]
    """
    pd = OrderedDict()
    if signature is None:
        spec = getfullargspec(function)
        i = - 1
        for a in spec.args:
            pd[a] = EMPTY
        for a in reversed(spec.args):
            try:
                pd[a] = spec.defaults[i]
            except IndexError:
                break
            i -= 1
    else:
        for pn, p in signature(function).parameters.items():
            if p.default is inspect.Parameter.empty:
                pd[pn] = EMPTY
            else:
                pd[pn] = p.default
    return pd


def read(data):
    # type: (Union[str, IOBase, addbase]) -> Any
    if (
        (hasattr(data, 'readall') and callable(data.readall)) or
        (hasattr(data, 'read') and callable(data.read))
    ):
        try:
            data.seek(0)
        except UnsupportedOperation:
            pass
        if hasattr(data, 'readall'):
            data = data.readall()
        else:
            data = data.read()
        return data
    else:
        raise TypeError(
            '%s is not a file-like object' % repr(data)
        )


if __name__ == '__main__':
    import doctest
    doctest.testmod()
