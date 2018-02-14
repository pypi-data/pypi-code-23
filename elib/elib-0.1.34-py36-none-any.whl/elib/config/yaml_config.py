# coding=utf-8
"""
Manages YAML configuration
"""

import collections
import os

import everett
import everett.manager
import yaml


def update_nested_dict(target_dict: collections.MutableMapping,
                       source_dict: collections.MutableMapping) -> collections.MutableMapping:
    """
    Updates a config dictionary that might contain other config dictionaries
    :param target_dict: dictionary to update
    :param source_dict: dictionary that contains values to use
    :return: updated target_dict
    """
    if source_dict is None:
        return target_dict
    for key, value in source_dict.items():
        if isinstance(value, collections.MutableMapping):
            target_dict[key.upper()] = update_nested_dict(
                target_dict.get(key, {}), value)
        else:
            target_dict[key.upper()] = source_dict[key]
    return target_dict


def flatten_dict(source_dict: collections.MutableMapping, parent_key='', sep='_') -> dict:
    """
    Flattens a dictionary, adding namespaces to key names
    :param source_dict: dictionary to flatten
    :param parent_key: namespace
    :param sep: separator to use, defaults to "_"
    :return: config dictionary
    """
    items = []
    for key, value in source_dict.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


class YAMLConfig:
    """
    Represents a Config coming from a YAML file
    """

    def __init__(self, possible_paths):
        self.cfg = {}
        possible_paths = everett.manager.listify(possible_paths)

        for path in possible_paths:
            if not path:
                continue

            path = os.path.abspath(os.path.expanduser(path.strip()))
            if path and os.path.isfile(path):
                self.cfg = update_nested_dict(
                    self.cfg, self.parse_yaml_file(path))

        self.cfg = flatten_dict(self.cfg)

    @staticmethod
    def parse_yaml_file(path: str) -> dict:
        """
        Reads a YAML file into a dictionary
        :param path: path to YAML file
        :return: dictionary
        """
        with open(path) as stream:
            return yaml.load(stream)

    def get(self, key, namespace=None):
        """
        Obtain a key value from the config dict
        :param key: key name
        :param namespace: namespace of the config key
        :return: config value
        """
        value = everett.manager.get_key_from_envs(self.cfg, key, namespace)
        return value
