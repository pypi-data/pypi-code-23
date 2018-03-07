import re

class SENTINAL():
    pass

def json_get_fast(json_string, key, default=SENTINAL()):
    '''
    uses regex to pull out the simple value of <key> in <json_string>, 
    without parsing the json object.  If <key> is not found
    return <default>, or if unspecified raise KeyError.

    Limitations:
        - <json_string> must be a plain json object e.g. '{"key":"val"...}'
        - the target value must be simple, e.g. null, number, or string
        - the first match for <key> (having a simple val) is returned 
            (it is ok if key arises within a nested object)

    Output:
        - all numbers are returned as floats. cast to int as desired.
        - null is returned as None
        - if the key is not found, KeyError is raised, unless <default>
            is specified, in which case <default> is returned
        - keys which have non-simple values (arrays or nested objects) are
            ignored (this can lead to KeyError if key is present but val
            is not simple).
    '''

    find_pattern = (
        r'"%s"'                    # match the key
        r'\s*:\s*'                # match the colon
        r'(null|[\d\.]+|".*?")'    # match the val (null, number, or string)
    ) % key
    find_re = re.compile(find_pattern)

    try:
        val_str = find_re.search(json_string).groups()[0]
    except (AttributeError, IndexError):
        if isinstance(default, SENTINAL):
            raise KeyError(key)
        else:
            return default

    if val_str == 'null':
        return None
    if val_str.startswith('"'):
        return val_str[1:-1]    # strip quotes
    return float(val_str)



