# *- coding: utf-8 -*-
""" utilities, prototypes and classes of parsers

_schemas.py - created on 02/01/2018
author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext

from ngomodel import JsonParser
from ngomodel import YamlParser
from ngomodel import register_parser

_ = gettext.gettext


@register_parser
class CookiecutterJsonParser(JsonParser):
    id = 'json_cc'
    object = "ngoproject.Cookiecutter"
    extensions = ['.json']

    def loads(stream):
        data = JsonParser.loads(stream)
        return data['cookiecutter']


@register_parser
class CookiecutterYamlParser(YamlParser):
    id = 'yaml_cc'
    object = "ngoproject.Cookiecutter"
    extensions = ['.yaml', '.yml', '.ngoproject']

    def loads(stream):
        data = YamlParser.loads(stream)
        return data['cookiecutter']
