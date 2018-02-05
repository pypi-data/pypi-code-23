#!/usr/bin/env python
# -*-encoding:utf-8-*-

import json


def load_json(_file):
    return load_file_to_obj(_file)


def load_file_to_obj(_file):
    f = file(_file)
    jsonobj = json.load(f)
    return jsonobj


def load_str_to_obj(str):
    return json.loads(str)


def dump_to_str(obj):
    return json.dumps(obj, ensure_ascii=False)
