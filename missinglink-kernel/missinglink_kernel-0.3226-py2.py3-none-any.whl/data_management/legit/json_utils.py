# -*- coding: utf8 -*-
import json
import os
import six
from .path_utils import enumerate_paths


def __get_json_items(data):
    if isinstance(data, dict):
        for key, val in data.items():
            val['_sha'] = key

            yield val
    else:  # list, generators
        for key, val in data:
            val['_sha'] = key

            yield val


def multi_line_json_from_data(data, write_to=None):
    result = write_to or six.BytesIO()
    for i, item in enumerate(__get_json_items(data)):
        json_str = json.dumps(item) + '\n'
        if six.PY3:
            json_str = json_str.encode()

        result.write(json_str)

    return result


def newline_json_file_from_json_file(datafile):
    json_data = json.load(datafile)
    return multi_line_json_from_data(json_data)


def json_data_from_files(data_path, files, data_per_entry):
    def rel_path_if_needed(path):
        if os.path.isabs(path):
            return os.path.relpath(path, data_path)

        return path

    for file_path in enumerate_paths(files):
        file_path = rel_path_if_needed(file_path)
        yield file_path, data_per_entry


def normalize_item(item):
    result_item = {}

    for key, val in item.items():
        if key == 'meta':
            continue

        result_item['@' + key] = val

    for key, val in item.get('meta', {}).items():
        result_item[key] = val

    return result_item
