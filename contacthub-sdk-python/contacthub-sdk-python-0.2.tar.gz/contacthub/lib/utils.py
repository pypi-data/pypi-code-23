# -*- coding: utf-8 -*-
import json
import datetime
from copy import deepcopy


class DateEncoder(json.JSONEncoder):
    """
    Class for JSON encoding datetime and date object.
    """
    def default(self, obj):
        """
        Serialize the given obj for JSON.

        :param obj: the object to serialize
        :return: a string ISO 8601 formatted
        """
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def get_dictionary_paths(d, main_list):
    """
    Set the given main_list with lists containing all the key-paths of a dictionary.
    For example: The key-paths for this list {a{b:{c:1, d:2}, e:3}} are a,b,c; a,b,d; a,e

    :param d: the dictionary for gaining all the depth path
    :param main_list: a list for creating al the lists containing the paths of the dictt
    """
    tmp_list = []
    _get_dictionary_paths(d, main_list=main_list, tmp_list=tmp_list)


def _get_dictionary_paths(d, main_list, tmp_list):
    """
    Private method for setting the given main_list with lists containing all the key-paths of a dictionary.
    For example: The key-paths of this list {a{b:{c:1, d:2}, e:3}} are a,b,c; a,b,d; a,e

    :param d: the dictionary for gaining all the depth path
    :param main_list: a list for creating al the lists containing the paths of the dictt
    :param tmp_list: a temporary list for inserting the actual path
    """
    for elem in d:
        if isinstance(d[elem], dict):
            tmp_list.append(elem)
            _get_dictionary_paths(d[elem], main_list=main_list, tmp_list=tmp_list)
            tmp_list.pop()
        else:
            tmp_list.append(elem)
            main_list.append(deepcopy(tmp_list))
            tmp_list.pop()


def generate_mutation_tracker(old_attributes, new_attributes):
    """
    Given old attributes of an entity and the new attributes in a Properties object, this method creates a new
    dictionary based on the whole old attributes dictionary, with:

    - the attributes in old_attributes updated with the attributes in new_attributes
    - the attributes not in new_attributes (deleted) setted to None

    :param old_attributes: The old attributes of an entity for create a mutation tracker dict updated
    :param new_attributes: The new attributes of an entity for create a mutation tracker dict updated
    :return: a dictionary with the mutation between old_attributes and new_attributes
    """
    main_list_of_paths = []

    get_dictionary_paths(old_attributes, main_list=main_list_of_paths)
    #  we start wih the whole old dictionary, next we will set the missing keys to None
    mutation_tracker = deepcopy(old_attributes)
    #  follow the paths for searching keys not in new properties but in the old ones (mutation_tracker)

    for key_paths in main_list_of_paths:
        np = new_attributes
        mt = mutation_tracker
        op = old_attributes
        for single_key in key_paths:
            if single_key not in np:
                if single_key in op and isinstance(op[single_key], list):
                    mt[single_key] = []
                else:
                    mt[single_key] = None
                break
            else:
                mt[single_key] = np[single_key]
                np = np[single_key]
                mt = mt[single_key]
                op = op[single_key]
    return mutation_tracker


def remove_empty_attributes(body):
    new = deepcopy(body)
    for key in body:
        if body[key] and isinstance(body[key], dict):
            new[key] = remove_empty_attributes(body[key])
        if body[key] and isinstance(body[key], list):
            for elem in new[key]:
                if isinstance(elem, dict):
                    new[key][new[key].index(elem)] = remove_empty_attributes(elem)
        if body[key] is None:
            new.pop(key)
    return new


def convert_properties_obj_in_prop(properties, properties_class):
    """
    Convert the internal properties of `properties_class` object in a dictionary.

    :param properties: the properties of a `properties_class` object to convert
    :param properties_class: if the internal properties of an object are instance of this class,
        we assign at the property the internal attributes instead of the object
    """
    for k in properties:
        if isinstance(properties[k], properties_class):
            properties[k] = properties[k].attributes
        if isinstance(properties[k], list):
            for elem in properties[k]:
                if isinstance(elem, properties_class):
                    index = properties[k].index(elem)
                    properties[k][index] = elem.attributes
        elif isinstance(properties[k], dict):
            convert_properties_obj_in_prop(properties=properties[k], properties_class=properties_class)


def resolve_mutation_tracker(mutation_tracker):
    """
    From a dictionary with comma separated keys (e.g. {'a.b.c.d': 'e'}), creates a new dictionary with nested
    dictionaries, each of which containing a key taken from comma separated keys. (e.g. {'a': {'b' {'c': {'d': 'e'}}}})

    :param mutation_tracker: the dictionary with comma separated keys
    :return: a new dictionary containing nested dictionaries with old comma separated keys
    """
    body = {}
    for key in mutation_tracker:
        update_dictionary = body
        splitted = key.split('.')
        for attr in splitted:
            if attr == splitted[-1]:
                update_dictionary[attr] = mutation_tracker[key]
            else:
                if attr not in update_dictionary:
                    update_dictionary[attr] = {}
                update_dictionary = update_dictionary[attr]
    return body
