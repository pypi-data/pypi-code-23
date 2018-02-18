import yaml
import functools32
import copy
import logging
import simplejson as json
import jsonschema
from flask import request, make_response
import werkzeug.exceptions

import python_jsonschema_objects as pjo


class SwaggerKeeper(object):
    def __init__(self):
        self._definitions = {}
        self._skipped = set()

        self._pjo_cache = dict()


    def route(**kwargs):
        validate = kwargs.pop("validate", False)

        def inner(fn):

            if validate:
                return self.validate_request_data(fn) 

            return wrapper

        inner = flask.route(**kwargs)(inner)

        return inner


    def define(self, name, schema):
        if isinstance(schema, basestring):
            schema = yaml.safe_load(schema)
        elif not isinstance(schema, dict):
            raise Exception("Definitions must be YAML or dict")

        self._definitions[name] = schema

    def validate_request_data(self, fn):
        swagger_desc = yaml.safe_load(fn.__doc__)

        consumer = swagger_desc.get('consumes', None)
        if consumer is not None and (len(consumer) != 1 or consumer[0] != 'application/json'):
            logging.error(
                "validate_request_data() decorator can only be "
                "used with a swagger definition that consumes json"
            )
            raise RuntimeError("Malformed endpoint description")

        schema = {
            "definitions": self._definitions,
            "$schema": "http://json-schema.org/draft-04/schema#",
        }
        params = [p for p
                  in swagger_desc['parameters']
                  if p['in'] == "body"]
        if len(params) > 1:
            logging.error("Only one body parameter is allowed")
            raise RuntimeError(
                "Malformed endpoint description")
        elif len(params) == 1:
            schema.update(params[0]['schema'])
            validator = jsonschema.Draft4Validator(schema)
        else:
            validator = None

        response_validators = {}
        for retcode, resp_desc in swagger_desc['responses'].iteritems():
            if 'schema' in resp_desc:
                resp_schema = {
                    "$schema": "http://json-schema.org/draft-04/schema#"
                }
                resp_schema.update(resp_desc['schema'])
                resp_schema['definitions'] = self._definitions

                response_validators[retcode] = resp_schema

        @functools32.wraps(fn)
        def wrapper(*args, **kwargs):
            errors = []
            if validator is not None:
# We only do this if the validator isn't None, because otherwise this 
# isn't JSON
                data = json.loads(request.data)
                for error in validator.iter_errors(data):
                    errors.append({
                        "error": error.message,
                        "at": "/".join(error.absolute_path)
                    })

                if len(errors) > 0:
                    err_resp = make_response(json.dumps(errors), 400)
                    err_resp.mimetype = 'application/json'
                    return err_resp

                resp = fn(data, *args, **kwargs)
            else:
                resp = fn(*args, **kwargs)

            if resp.status_code not in swagger_desc['responses']:
                logging.error(
                    "{2} returned invalid response '{0}'. "
                    "Valid responses: {1}".format(
                        resp.status_code,
                        swagger_desc['responses'].keys(),
                        request.path
                    )
                )
                raise werkzeug.exceptions.InternalServerError(
                    "Invalid handler response")

            resp_schema = response_validators.get(resp.status_code, None)
            if resp_schema is not None:
                resp_validator = jsonschema.Draft4Validator(resp_schema)
                response_data = json.loads(resp.get_data())
                has_error = False
                for error in resp_validator.iter_errors(response_data):
                    has_error = True
                    logging.error("Invalid response: {0}".format(error))

                if has_error:
                    return make_response("Invalid response", 500)

            return resp

        return wrapper

    def skip(self, fn):
        self._skipped.add(fn.__name__)
        return fn

    def schema(self, name):
        if name not in self._definitions:
            raise KeyError(
                "'{0}' is not defined"
                .format(name))

        schema = {}
        schema.update(self._definitions[name])
        schema['title'] = name
        schema['definitions'] = {
            n: self._definitions[n]
            for n in self._definitions
        }

        return copy.deepcopy(schema)

    def classgen(self, name):
        if name not in self._definitions:
            raise KeyError(
                "'{0}' is not defined"
                .format(name))

        if name not in self._pjo_cache:
            schema = self.schema(name)
            builder = pjo.ObjectBuilder(schema)
            builder.build_classes()
            self._pjo_cache[name] = builder.get_class(name)

        return self._pjo_cache[name]


registry = SwaggerKeeper()
