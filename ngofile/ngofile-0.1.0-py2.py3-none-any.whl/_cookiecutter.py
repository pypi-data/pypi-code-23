# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 11:06:57 2012

@author: cedric
"""
from __future__ import unicode_literals

from builtins import object
from builtins import str

from ngomodel import ClassWithSchema
from ngomodel import ObjectManager
from ngomodel import register_parser
from ngomodel import take_arrays

from ngomodel._json import JsonParser
from ngomodel._yaml import YamlParser


class Cookiecutter(ClassWithSchema):
    schemaPath = "schemas/Cookiecutter.json"


@register_parser
class CookiecutterJsonParser(JsonParser):
    id = 'json_cc'
    extensions = ['.json']

    @take_arrays(1)
    def loads(self, stream, **kwargs):
        data = JsonParser.loads(self, stream, **kwargs)
        if 'cookiecutter' in data:
            data = data['cookiecutter']
        return data


@register_parser
class CookiecutterYamlParser(YamlParser):
    id = 'yaml_cc'
    extensions = ['.yaml', '.yml', '.ngocc']

    @take_arrays(1)
    def loads(self, stream, **kwargs):
        data = YamlParser.loads(self, stream, **kwargs)
        if 'default_context' in data:
            data = data['default_context']
        return data


class CookiecutterManager(ObjectManager):
    extensions = ['.ngocc']
    parsers = [CookiecutterJsonParser, CookiecutterYamlParser]

    def __init__(self, *args, **kwargs):
        ObjectManager.__init__(self, Cookiecutter, *args, **kwargs)
