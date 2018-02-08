import contextlib
import functools

from jsonschema.validators import Draft4Validator, RefResolver
from six import iteritems
from six.moves.urllib.request import urlopen
from swagger_spec_validator import ref_validators
from swagger_spec_validator.validator20 import (deref, validate_apis,
                                                validate_definitions)
from yaml import safe_load


def validate_spec_url(spec_url, schema_url=''):
    return validate_spec(read_url(spec_url), schema_url, spec_url)


def read_url(url, timeout=1):
    with contextlib.closing(urlopen(url, timeout=timeout)) as fh:
        return safe_load(fh.read().decode('utf-8'))


def validate_spec(spec_dict, schema_url, spec_url=''):
    openapi_resolver = validate_json(spec_dict,
                                     schema_url,
                                     spec_url)
    bound_deref = functools.partial(deref, resolver=openapi_resolver)
    spec_dict = bound_deref(spec_dict)
    apis = _apis_defs_getter(spec_dict['paths'], bound_deref)
    definitions = _apis_defs_getter(spec_dict.get('definitions', {}),
                                    bound_deref)

    validate_apis(apis, bound_deref)
    validate_definitions(definitions, bound_deref)

    return openapi_resolver


def validate_json(spec_dict, schema_url, spec_url=''):
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
