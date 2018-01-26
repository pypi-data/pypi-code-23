"""Loaders for `:py:class:~collections.OrderedDict`."""

from __future__ import print_function, division, absolute_import

import yaml

from collections import OrderedDict

__all__ = []


def construct_yaml_map(self, node):
    data = OrderedDict()
    yield data
    value = self.construct_mapping(node)
    data.update(value)


def construct_mapping(self, node, deep=False):
    if isinstance(node, yaml.MappingNode):
        self.flatten_mapping(node)
    else:
        msg = 'Expected a mapping node, but found {}'.format(node.id)
        raise yaml.constructor.ConstructError(None, None, msg, node.start_mark)

    mapping = OrderedDict()
    for key_node, value_node in node.value:
        key = self.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as err:
            raise yaml.constructor.ConstructError('while constructing a mapping', node.start_mark,
                                                  'found unacceptable key ({})'.format(err),
                                                  key_node.start_mark)
        value = self.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping


class OrderedLoaderMixin(object):
    def __init__(self, *args, **kwargs):
        super(OrderedLoaderMixin, self).__init__(*args, **kwargs)

        self.add_constructor('tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor('tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    construct_yaml_map = construct_yaml_map
    construct_mapping = construct_mapping


class Loader(OrderedLoaderMixin, yaml.Loader):
    pass


class SafeLoader(OrderedLoaderMixin, yaml.SafeLoader):
    pass


class CLoader(OrderedLoaderMixin, yaml.CLoader):
    pass


class CSafeLoader(OrderedLoaderMixin, yaml.CSafeLoader):
    pass
