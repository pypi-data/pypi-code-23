# -*- coding: utf-8 -*-
from __future__ import absolute_import

from six import text_type

__author__ = 'lundberg'


def normalize_whitespace(s):
    """
    Removes leading and ending whitespace from a string.
    """
    return ' '.join(s.split())


def lowerstr(s):
    """
    Makes everything to a string and tries to make it lower case. Also
    normalizes whitespace.
    """
    return normalize_whitespace(text_type(s).lower())


def update_item_properties(item_properties, new_properties):
    for key, value in new_properties.items():
        if value or value is 0:
            item_properties[key] = value
        elif key in item_properties.keys():
            del item_properties[key]
    return item_properties


# TODO: Does this helper make any sense?
def merge_properties(item_properties, prop_name, merge_value):
    """
    Tries to figure out which type of property value that should be merged and
    invoke the right function.
    Returns new properties if the merge was successful otherwise False.
    """
    existing_value = item_properties.get(prop_name, None)
    if not existing_value:  # A node without existing values for the property
        item_properties[prop_name] = merge_value
    else:
        if type(merge_value) is int or type(merge_value) is str:
            item_properties[prop_name] = existing_value + merge_value
        elif type(merge_value) is list:
            item_properties[prop_name] = merge_list(existing_value, merge_value)
        else:
            return False
    return item_properties


def merge_list(existing_value, new_value):
    """
    Takes the name of a property, a list of new property values and the existing
    node values.
    Returns the merged properties.
    """
    new_set = set(existing_value + new_value)
    return list(new_set)
