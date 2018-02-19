#!/usr/bin/python3

def _merge_list(list1, list2):
    list1.extend(list2)

def _merge_dict(dict1, dict2):
    for key, value2 in dict2.items():
        value1 = dict1.get(key)

        if (type(value1) is dict) and (type(value2) is dict):
            _merge_dict(value1, value2)
        elif (type(value1) is list) and (type(value2) is list):
            _merge_list(value1, value2)
        else:
            dict1[key] = value2

class VariableSet(object):
    def __init__(self):
        self.data = {}

    def _add_file(self, json_path):
        from json import load
        from os import stat

        if json_path.endswith('.json'):
            if stat(json_path).st_size < 1024*1024:
                with open(json_path, 'rb') as json_file:
                    json = load(json_file)

                    if type(json) is dict:
                        _merge_dict(self.data, json)

    def add_path(self, path):
        from os import walk
        from os.path import isdir
        from os.path import isfile
        from os.path import join

        if isdir(path):
            for root_path, _, file_paths in walk(path):
                for file_path in file_paths:
                    self._add_file(join(root_path, file_path))
        elif isfile(path):
            self._add_file(path)
