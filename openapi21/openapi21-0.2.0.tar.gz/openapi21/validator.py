import contextlib
import functools
import os

from jsonschema.validators import Draft4Validator, RefResolver
from six import iteritems, itervalues
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.request import urlopen
from swagger_spec_validator import ref_validators
from swagger_spec_validator.validator20 import (deref, validate_apis,
                                                validate_definitions)
from yaml import safe_load

from openapi21 import SCHEMA_URL


def validate_spec_url(spec_url, schema_url=SCHEMA_URL,
                      spec_url_base_path=None,
                      schema_url_base_path=None):
    spec_url = _normalize_url(spec_url, spec_url_base_path)
    return validate_spec(read_url(spec_url), schema_url, spec_url,
                         spec_url_base_path, schema_url_base_path)


def _normalize_url(url, url_base_path):
    if url_base_path is None:
        url_base_path = os.getcwd()
    elif not os.path.isabs(url_base_path):
            raise ValueError("The 'base_path' must be an absolute path")

    if url and not urlsplit(url).scheme:
        if not os.path.isabs(url):
            url = os.path.join(url_base_path, url)

        url = 'file:' + url

    return url


def read_url(url, timeout=1):
    with contextlib.closing(urlopen(url, timeout=timeout)) as fh:
        return safe_load(fh.read().decode('utf-8'))


def validate_spec(spec_dict, schema_url=SCHEMA_URL, spec_url='',
                  spec_url_base_path=None, schema_url_base_path=None):
    openapi_resolver = validate_json(spec_dict, schema_url, spec_url,
                                     spec_url_base_path,
                                     schema_url_base_path)
    bound_deref = functools.partial(deref, resolver=openapi_resolver)
    spec_dict = bound_deref(spec_dict)
    apis = _apis_defs_getter(spec_dict['paths'], bound_deref)
    definitions = _apis_defs_getter(spec_dict.get('definitions', {}),
                                    bound_deref)

    validate_apis(apis, bound_deref)
    _validate_apis_parameters(apis, bound_deref)
    validate_definitions(definitions, bound_deref)

    return openapi_resolver


def validate_json(spec_dict, schema_url=SCHEMA_URL, spec_url='',
                  spec_url_base_path=None, schema_url_base_path=None):
    spec_url, schema_url = _normalize_urls(spec_url, schema_url,
                                           spec_url_base_path,
                                           schema_url_base_path)
    schema = read_url(schema_url)
    handlers = {
        'http': read_url,
        'https': read_url,
        'file': read_url,
    }
    schema_resolver = RefResolver(
        base_uri=schema_url,
        referrer=schema,
        handlers=handlers
    )
    spec_resolver = RefResolver(
        base_uri=spec_url,
        referrer=spec_dict,
        handlers=handlers
    )
    ref_validators.validate(
        instance=spec_dict,
        schema=schema,
        resolver=schema_resolver,
        instance_cls=ref_validators.create_dereffing_validator(spec_resolver),
        cls=Draft4Validator
    )

    return spec_resolver


def _normalize_urls(spec_url, schema_url,
                    spec_url_base_path,
                    schema_url_base_path):
    spec_url = _normalize_url(spec_url, spec_url_base_path)
    schema_url = _normalize_url(schema_url, schema_url_base_path)
    return spec_url, schema_url


def _apis_defs_getter(object_, deref):
    new_object = {}
    for key, value in iteritems(object_):
        value = deref(value)
        if key == 'allOf':
            for all_of_i in value:
                for key_i, value_i in iteritems(deref(all_of_i)):
                    new_object[key_i] = deref(value_i)
        else:
            new_object[key] = value

    return deref(new_object)


def _validate_apis_parameters(apis, deref):
    for api_name, api_body in iteritems(apis):
        base_uri = _get_base_uri(api_body)
        api_body = deref(api_body)

        base_uri = _get_base_uri(api_body.get('parameters'), base_uri)
        api_params = deref(api_body.pop('parameters', []))

        _validate_parameters(api_params, deref, api_name, 'all', base_uri)

        for oper_name in api_body:
            if oper_name.startswith('x-'):
                continue
            else:
                base_uri = _get_base_uri(api_body[oper_name], base_uri)
                oper_body = deref(api_body[oper_name])

                base_uri = _get_base_uri(oper_body.get('parameters'), base_uri)
                oper_params = deref(oper_body.get('parameters', []))

                _validate_parameters(oper_params, deref, api_name,
                                     oper_name, base_uri)


def _get_base_uri(object_, base_uri=''):
    if isinstance(object_, dict) and '$ref' in object_:
        return object_['x-scope'][-1]
    else:
        return base_uri


def _validate_parameters(parameters, deref, api_path, api_method, base_uri):
    for param in parameters:
        base_uri = _get_base_uri(param, base_uri)
        param = deref(param)

        base_uri = _get_base_uri(param.get('example'), base_uri)
        example = deref(param.get('example'))

        base_uri = _get_base_uri(param.get('examples'), base_uri)
        examples = deref(param.get('examples'))

        if example or examples:
            if example:
                examples = {None: example}

            if param.get('type') == 'object' or param['in'] == 'body':
                schema = param['schema']
            else:
                schema = _get_schema_from_param(param)

            _validate_parameter_examples(schema, examples, base_uri)


def _get_schema_from_param(param):
    schema = param.copy()
    schema.pop('name', None)
    schema.pop('in', None)
    schema.pop('required', None)
    return schema


def _validate_parameter_examples(schema, examples, base_uri):
    handlers = {
        'http': read_url,
        'https': read_url,
        'file': read_url,
    }

    base_uri = _get_base_uri(schema, base_uri)
    spec_resolver = RefResolver(base_uri, schema, handlers=handlers)

    for example in itervalues(examples):
        ref_validators.validate(
            instance=example,
            schema=schema,
            resolver=spec_resolver,
            instance_cls=ref_validators.create_dereffing_validator(
                spec_resolver),
            cls=Draft4Validator
        )
