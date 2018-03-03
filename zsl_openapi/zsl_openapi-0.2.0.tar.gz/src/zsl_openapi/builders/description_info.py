from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from builtins import *  # NOQA
from collections import namedtuple
from typing import Any  # NOQA
from typing import Dict  # NOQA

import yaml
from zsl.utils.string_helper import camelcase_to_underscore

from zsl_openapi.api import ApiDescription  # NOQA
from zsl_openapi.api import ApiModelDefinition
from zsl_openapi.api import ApiModelProperty
from zsl_openapi.api import ApiTag
from zsl_openapi.api import SecurityDefinitions
from zsl_openapi.builders import ApiDescriptionBuilder


def fill(yaml_spec, api_description):
    # type: (Dict[str, Any]|str, ApiDescription)->None
    def fill_dict(dict_obj, api_obj, hint):
        # type: (Dict, Any)->None
        for k, v in dict_obj.items():
            if hint.type is None:
                logging.getLogger(__name__).debug('Setting {0} to {1}'.format(camelcase_to_underscore(k), v))
                fill(v, api_obj, camelcase_to_underscore(k), hint)
            else:
                inner_api_obj = hint.type()
                inner_api_obj.name = k
                fill_dict(v, inner_api_obj, hint.hints)
                getattr(api_obj, hint.appender)(inner_api_obj)

    def fill_list(list_obj, api_obj, hint):
        for v in list_obj:
            inner_api_obj = hint.type()
            fill_dict(v, inner_api_obj, hint.hints)
            getattr(api_obj, hint.appender)(inner_api_obj)

    def fill(obj, api_obj, property_name, hint):
        if isinstance(obj, dict):
            if property_name in hint.hints:
                fill_dict(obj, api_obj, hint.hints[property_name])
            else:
                fill_dict(obj, getattr(api_obj, property_name), hint)
        elif isinstance(obj, list):
            fill_list(obj, api_obj, hint.hints[property_name])
        else:
            setattr(api_obj, PROPERTY_MAP.get(property_name, property_name), obj)

    Hint = namedtuple('Hint', ['type', 'appender', 'hints'])

    EMPTY_HINT = Hint(None, None, {})

    HINTS = Hint(None, None, {
        'tags': Hint(ApiTag, 'add_tag', EMPTY_HINT),
        'definitions': Hint(ApiModelDefinition, 'add_model_definition', Hint(None, None, {
            'properties': Hint(ApiModelProperty, 'add_property', EMPTY_HINT)
        })),
        'security_definitions': Hint(SecurityDefinitions, 'set_security_definitions', EMPTY_HINT)
    })

    PROPERTY_MAP = {
        '$ref': 'ref'
    }

    if isinstance(yaml_spec, dict):
        yaml_dict = yaml_spec
    elif isinstance(yaml_spec, str):
        yaml_dict = yaml.load(yaml_spec)
    else:
        raise TypeError("When filling OpenAPI only dict/str/unicode may be parsed.")

    if 'paths' in yaml_dict:
        del yaml_dict['paths']

    fill_dict(yaml_dict, api_description, HINTS)


class FileApiDescriptionInfoBuilder(ApiDescriptionBuilder):
    def __init__(self, description):
        # type: (str)->None
        with open(description, 'rb') as f:
            self._loaded_spec = yaml.load(f)

    def build(self, api_description):
        fill(self._loaded_spec, api_description)
