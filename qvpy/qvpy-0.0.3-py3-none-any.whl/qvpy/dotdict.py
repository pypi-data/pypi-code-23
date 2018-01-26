# -*- coding: utf-8 -*-

### imports ###################################################################
import logging

### logging ###################################################################
logging.getLogger('dotDict').addHandler(logging.NullHandler())


###############################################################################
def getChildren(parent):

    children = []
    values = []

    for key in parent.keys():
        attr = getattr(parent, key)

        if type(attr) in [bool, int, float, str, list]:
            values.append(key)
        else:
            children.append(key)

    return values, children


###############################################################################
def substitute(parent, substitutions):

    keys_to_values, keys_to_groups = getChildren(parent)

    for key in keys_to_values:
        value = getattr(parent, key)

        if type(value) == str and '$' in value:
            value = value.replace('$', '')

            evaluated = eval(value, substitutions)

            logging.getLogger('dotDict').debug(
                'Evaluated %s: %s = %s', key, value, evaluated)

            setattr(parent, key, evaluated)

    for key in keys_to_groups:
        group = getattr(parent, key)
        substitute(group, substitutions)


###############################################################################
class DictWithAttributes(dict):
    def __init__(self, inDict=None):
        super(DictWithAttributes, self).__init__(inDict)

        for key, value in inDict.items():
            setattr(self, key, None)

            if type(value) == dict:
                setattr(self, key, DictWithAttributes(value))
            else:
                setattr(self, key, value)
