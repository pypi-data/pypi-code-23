import re
import sys

__version_info__ = (0, 2, 1)
__version__ = '.'.join(map(str, __version_info__))

ReType = type(re.compile(''))


def is_string(obj):
    '''
    Check if ``obj`` is a string
    '''
    return isinstance(obj, str)


def is_regex(obj):
    '''
    Check if ``obj`` is a regular expression
    
    '''
    return isinstance(obj, ReType)


def replace(text, old, new, count=None, strip=False):
    '''
    Replace an ``old`` subset of ``text`` with ``new``.
    
    ``old`` type may be either a string or regular expression.
    
    If ``strip``, remove all leading/trailing whitespace.
    
    If ``count``, replace the specified number of occurence, otherwise replace all.
    '''
    if is_string(old):
        text = text.replace(old, new, -1 if count is None else count)
    else:
        text = old.sub(new, text, 0 if count is None else count)
    
    if strip:
        text = text.strip(None if strip == True else strip)
    
    return text


def remove(text, what, count=None, strip=False):
    '''
    Like ``replace``, where ``new`` replacement is an empty string.
    '''
    return replace(text, what, '', count=count, strip=strip)


def replace_each(text, items, count=None, strip=False):
    '''
    Like ``replace``, where each occurrence in ``items`` is a 2-tuple of 
    ``(old, new)`` pair.
    '''
    for a,b in items:
        text = replace(text, a, b, count=count, strip=strip)
    return text


def remove_each(text, items, count=None, strip=False):
    '''
    Like ``remove``, where each occurrence in ``items`` is ``what`` to remove.
    '''
    for item in items:
        text = remove(text, item, count=count, strip=strip)
    return text


# TODO: not sure if ``contains`` is appropriate, maybe ``matches``?
def matches(text, what):
    '''
    Check if ``what`` occurs in ``text``
    
    '''
    return text.find(what) > -1 if is_string(what) else what.match(text)

contains = matches

def find_first(data, what):
    '''
    Search for ``what`` in the iterable ``data`` and return the index of the 
    first match. Return ``None`` if no match found.
    '''
    for i, line in enumerate(data):
        if contains(line, what):
            return i
            
    return None


def splitter(text, token=None, expected=2, default='', strip=False):
    '''
    Split ``text`` by ``token`` into at least ``expected`` number of results.
    
    When ``token`` is ``None``, the default for Python ``str.split`` is used, 
    which will split on all whitespace.
    
    ``token`` may also be a regex.
    
    If actual number of results is less than ``expected``, pad with ``default``.
    
    If ``strip``, than do just that to each result.
    '''
    if is_string(token) or token is None:
        bits = text.split(token, expected - 1)
    else:
        bits = [s for s in token.split(text, expected) if s]
        
    if strip:
        bits = [s.strip() for s in bits]
    
    n = len(bits)
    while n < expected:
        bits.append(default)
        n += 1
    
    return bits

