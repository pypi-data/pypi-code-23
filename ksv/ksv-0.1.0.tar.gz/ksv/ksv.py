# -*- coding: utf-8 -*-

"""Main module."""

import yaml
import base64


def show_yaml(fin, encode):
    y = yaml.load(fin)
    data_node = y['data']
    for k in data_node:
        v = data_node[k]
        if encode:
            new_v = base64.b64encode(str.encode(v)).decode()
            data_node[k] = new_v
        else:
            new_v = base64.b64decode(v).decode()
            data_node[k] = new_v
    print(yaml.dump(y, explicit_start=True, default_flow_style=False))
