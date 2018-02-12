import keyword
from re import sub, match

def to_caterpillar_case(camel_cased_string: str) -> str:
    """Replace UpperCase with upper-case and upperCase_Name with upper-case-name and splits into the dictionary levels

    :param str camel_cased_string: CamelCasedString to convert
    :rtype: str
    :returns: caterpillar-cased-string
    """
    if match(r".*[a-z](ID).*", camel_cased_string):
        camel_cased_string = camel_cased_string.replace("ID", "Id")
    return sub('(?<!^)(?=[A-Z])', '-', camel_cased_string).replace("_", "-").lower().split(".")[-1]


def to_snake_case(camel_cased_string: str) -> str:
    """Replace UpperCase with upper-case and upperCase_Name with upper_case_name and splits into the dictionary levels

    :param str camel_cased_string: CamelCasedString to convert
    :rtype: str
    :returns: snake_cased_string
    """
    if match(r".*[a-z](ID).*", camel_cased_string):
        camel_cased_string = camel_cased_string.replace("ID", "Id")
    return sub('(?<!^)(?=[A-Z])', '_', camel_cased_string).lower().split(".")[-1]


def to_camel_case(snake_cased_string: str) -> str:
    """Turns snake_cased_strings into snakeCasedStrings, reversing to_snake_case

    :param str snake_cased_string: snake_cased_string to convert
    :returns: camelCasedString
    """
    first, *others = snake_cased_string.split("_")

    # Turn ID back into uppercase
    return sub(r'(?<=[a-z])(Id)(?=[A-Za-z_]|$)',
               lambda match: match[1].upper(),
               ''.join([first.lower(), *map(str.title, others)]))


def python_name_for(javascript_type: str) -> str:
    """Find the Python name for a javascript type
    
    :param str javascript_type: JavaScript type name, e.g array, string, integer
    :returns: Name for the type in python
    :rtype: str
    """
    alternatives = {
        'integer': 'int',
        'number': 'int',
        'float': 'float',
        'object': 'dict',
        'array': 'list',
        'bool': 'bool',
        'boolean': 'bool',
        'string': 'str',
        'null': 'None'
    }

    if javascript_type in alternatives:
        return alternatives[javascript_type.lower()]
    else:
        return javascript_type

def to_safe_name(argument: str) -> str:
    """Python prevents us from using the built-in keywords as parameter names in
    functions, so if the API requests any of these keywords, we escape them with
    an underscore and provide a method to escape and unescape them

    :param str argument: Argument name to escape, if necessary
    :returns: _argument if the argument was unsafe
    """
    if keyword.iskeyword(argument):
        return "_%s" % argument
    return argument

def from_safe_name(argument: str) -> str:
    """Python prevents us from using the built-in keywords as parameter names in
    functions, so if the API requests any of these keywords, we escape them with
    an underscore and provide a method to escape and unescape them

    :param str argument: Argument name to escape, if necessary
    :returns: _argument if the argument was unsafe
    """
    if argument.startswith("_") and keyword.iskeyword(argument.replace("_", "")):
        return argument.replace("_", "")
    return argument