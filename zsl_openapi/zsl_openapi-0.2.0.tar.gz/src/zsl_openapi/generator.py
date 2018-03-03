from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA
from io import TextIOWrapper  # NOQA
from typing import IO  # NOQA
from typing import Any  # NOQA
from typing import Dict  # NOQA
from typing import List  # NOQA
from typing import Optional  # NOQA

import yaml
from zsl.utils.string_helper import underscore_to_camelcase

from zsl_openapi.api import ApiDescription  # NOQA
from zsl_openapi.api import ApiExternalDocs  # NOQA
from zsl_openapi.api import ApiModelDefinition  # NOQA
from zsl_openapi.api import ApiOperation  # NOQA
from zsl_openapi.api import ApiPathItem  # NOQA
from zsl_openapi.api import ApiTag  # NOQA
from zsl_openapi.api import SecurityDefinitions  # NOQA

Accumulator = Dict[str, Any]


class ApiGenerator(object):
    """Generates a dictionary suitable for YAML/JSON serialization out of the
    given ::class:`zsl_openapi.api.ApiDescription`."""

    def generate(self, api_description, output):
        # type: (ApiDescription, IO[str]|TextIOWrapper)->None
        accumulator = {}  # type: Accumulator
        self._write_header(accumulator)
        self._write_info(api_description, accumulator)
        self._write_definitions(api_description, accumulator)
        self._write_external_docs(api_description.external_docs, accumulator)
        self._write_tags(api_description, accumulator)
        self._write_paths(api_description, accumulator)
        self._write_security_definitions(api_description.security_definitions, accumulator)
        yaml.safe_dump(accumulator, output, encoding='utf-8', allow_unicode=True, default_flow_style=False)

    def _write_header(self, accumulator):
        # type: (Accumulator)->None
        accumulator['swagger'] = '2.0'

    def _write_info(self, api_description, accumulator):
        # type:(ApiDescription,  Accumulator)->Accumulator
        accumulator_info = {}  # type: Accumulator
        self._write_properties(api_description.info, accumulator_info, ['description', 'version', 'terms_of_service',
                                                                        'title'])
        self._write_info_license(api_description, accumulator_info)
        self._write_info_contact(api_description, accumulator_info)
        self._write_value('info', accumulator_info, accumulator)
        return accumulator_info

    def _write_info_contact(self, api_description, accumulator_info):
        # type:(ApiDescription,  Accumulator)->Accumulator
        accumulator_info_contact = {}  # type: Accumulator
        self._write_properties(api_description.info.contact, accumulator_info_contact, ['email'])
        self._write_value('contact', accumulator_info_contact, accumulator_info)
        return accumulator_info_contact

    def _write_info_license(self, api_description, accumulator_info):
        # type:(ApiDescription,  Accumulator)->Accumulator
        accumulator_info_license = {}  # type: Accumulator
        self._write_properties(api_description.info.license, accumulator_info_license, ['name', 'url'])
        self._write_value('license', accumulator_info_license, accumulator_info)
        return accumulator_info_license

    def _write_definitions(self, api_description, accumulator):
        # type:(ApiDescription,  Accumulator)->Accumulator
        accumulator_definitions = {}  # type: Accumulator
        for model_definition in api_description.definitions.values():
            self._write_model_definition(model_definition, accumulator_definitions)
        self._write_value('definitions', accumulator_definitions, accumulator)
        return accumulator_definitions

    def _write_model_definition(self, api_definition, accumulator_definitions):
        # type: (ApiModelDefinition, Accumulator)->Accumulator
        accumulator_definition = {}  # type: Accumulator
        self._write_properties(api_definition, accumulator_definition, ['type'])

        accumulator_properties = {}  # type: Accumulator
        for model_property in api_definition.properties.values():
            accumulator_property = {}  # type: Accumulator
            self._write_properties(model_property, accumulator_property, ['type', 'format'])
            accumulator_property_items = {}
            self._write_properties(model_property.items, accumulator_property_items, ['type', 'ref'], {'ref': '$ref'})
            self._write_value('items', accumulator_property_items, accumulator_property)
            self._write_value(model_property.name, accumulator_property, accumulator_properties)

        self._write_value('properties', accumulator_properties, accumulator_definition)
        self._write_value(api_definition.name, accumulator_definition, accumulator_definitions)
        return accumulator_definition

    def _write_external_docs(self, api_description, accumulator):
        # type: (ApiExternalDocs,  Accumulator)->Accumulator
        accumulator_external_docs = {}  # type:Accumulator
        self._write_properties(api_description, accumulator_external_docs, ['description', 'url'])
        self._write_value('externalDocs', accumulator_external_docs, accumulator)
        return accumulator_external_docs

    def _write_tags(self, api_description, accumulator):
        # type: (ApiDescription, Accumulator)->List[Accumulator]
        accumulator_tags = []  # type: List[Accumulator]
        for tag in api_description.tags:
            self._write_tag(tag, accumulator_tags)
        self._write_value('tags', accumulator_tags, accumulator)
        return accumulator_tags

    def _write_tag(self, tag, accumulator_tags):
        # type:  (ApiTag, List[Accumulator])->Accumulator
        accumulator_tag = {}  # type: Accumulator
        self._write_properties(tag, accumulator_tag, ['name', 'description'])
        self._write_external_docs(tag.external_docs, accumulator_tag)
        accumulator_tags.append(accumulator_tag)
        return accumulator_tag

    def _write_paths(self, api_description, accumulator):
        # type: (ApiDescription, Accumulator)->None
        paths_accumulator = {}
        for url, path in api_description.paths.items():
            self._write_path(url, path, paths_accumulator)
        self._write_value('paths', paths_accumulator, accumulator)

    def _write_path(self, url, api_path, accumulator):
        # type: (str, ApiPathItem, Accumulator)->None
        operation = {}
        accumulator[url] = {
            'post': operation
        }
        self._write_api_operation(api_path.post, operation)

    def _write_api_operation(self, operation, accumulator):
        # type: (ApiOperation, Accumulator)->None
        self._write_properties(operation, accumulator, ['description', 'summary', 'operation_id', 'produces', 'tags'])
        self._write_single_property(operation, accumulator, 'request_body')
        self._write_single_property(operation, accumulator, 'parameters')
        accumulator['responses'] = responses = {}
        for status_code, response in operation.responses.items():
            response_accumulator = {}
            responses[status_code] = response_accumulator
            self._write_properties(response, response_accumulator, ['content', 'schema', 'description'])

    def _write_properties(self, api_obj, accumulator, properties, result_property_names=None):
        # type: (object, Accumulator, List[str], Dict[str, str])->None
        if result_property_names is None:
            result_property_names = {}
        for property_name in properties:
            result_property_name = ApiGenerator._get_result_property_name(property_name)
            result_property_name = result_property_names.get(property_name, result_property_name)
            self._write_single_property(api_obj, accumulator, property_name, result_property_name)

    def _write_single_property(self, api_obj, accumulator, property_name, result_property_name=None):
        # type: (object, Accumulator, str, str)->None
        if result_property_name is None:
            result_property_name = self._get_result_property_name(property_name)

        value = getattr(api_obj, property_name)

        ApiGenerator._write_value(result_property_name, value, accumulator)

    @staticmethod
    def _get_result_property_name(property_name):
        # type: (str)->str
        return underscore_to_camelcase(property_name, False)

    @staticmethod
    def _write_value(property_name, value, accumulator):
        # type: (str, Any, Accumulator)->None
        if not value:
            return

        accumulator[property_name] = value

    @staticmethod
    def _write_security_definitions(security_definitions, accumulator):
        # type: (Optional[SecurityDefinitions], Accumulator)->None
        if security_definitions is None:
            return

        api_key = security_definitions.api_key
        sd_accumulator = {}
        ApiGenerator._write_value('api_key', api_key.__dict__, sd_accumulator)
        ApiGenerator._write_value('security_definitions', sd_accumulator, accumulator)
