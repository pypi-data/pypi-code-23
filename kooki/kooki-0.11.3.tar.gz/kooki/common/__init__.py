from collections import OrderedDict

from .metadata import *
from .template import *


def apply_custom(parts, custom):
    print('apply custom')
    result = []
    for index, part in enumerate(parts):
        result.append(custom(part, index))
    return result


def apply_merge(data):
    print('apply merge')
    result = None

    if isinstance(data, list):
        result = ''
        for content in data:
            result += content

    elif isinstance(data, OrderedDict):
        result = ''
        for key, content in OrderedDict(data).items():
            result += content

    else:
        raise Exception('merging bad data type {}'.format(type(data)))

    return result


def apply_split(data, separator):
    print('apply split')
    parts = data.split(separator)
    return parts
