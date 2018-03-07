from collections import OrderedDict

import yaml


class Loader(yaml.Loader):

    def construct_yaml_map(self, node):
        data = OrderedDict()
        data.start_mark = node.start_mark
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        return OrderedDict(self.construct_pairs(node, deep=deep))


yaml.add_constructor(
    'tag:yaml.org,2002:map',
    Loader.construct_yaml_map,
    Loader=Loader)


class Dumper(yaml.Dumper):

    def ignore_aliases(self, *args):
        return True

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode('tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)
