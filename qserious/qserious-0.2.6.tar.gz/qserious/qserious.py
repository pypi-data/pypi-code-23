# QueryString deserializer

import re
import urllib

def setKey (o, keys, value):
    if( len(keys) > 1 ):
        o[keys[0]] = {}
        setKey(o[keys[0]], keys[1:], value)
    else:
        o[keys[0]] = value

def bracketsToDots (text):
    return re.sub(r"\]\[|\[|\]", ".", re.sub(r"\]$", "", re.sub(r"^\[", "", text)) )

def deserialize(qs):
    if( not isinstance(qs, str) ):
        raise TypeError('should be a string')

    params = qs.split('&')
    result = {}

    for param in params:
        parts = param.split('=')
        setKey(result, bracketsToDots(parts[0]).split('.'), urllib.unquote(parts[1]) )

    return result

def keysTobrackets (keys):
    result = ''
    for i, key in enumerate(keys):
        if i > 0:
            result += '[' + key + ']'
        else:
            result += key
    return result

def _serialize (data, params, keys):
    iterable = False
    try:
        iter(data)
        iterable = True
    except:
        pass

    if not iterable or isinstance(data, str):
        params.append( keysTobrackets(keys) + '=' + urllib.quote( str(data), safe='~()*!.\'') )
        return

    for k in data:
        _keys = keys[:]
        _keys.append(k)
        _serialize( data[k], params, _keys )

def serialize (data):
    params = []
    _serialize(data, params, [])
    return '&'.join(params)


__all__ = ['deserialize', 'setKey', 'bracketsToDots', 'keysTobrackets']
