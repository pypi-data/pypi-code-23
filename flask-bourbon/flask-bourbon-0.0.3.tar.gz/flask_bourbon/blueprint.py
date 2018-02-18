# coding: utf8
import operator
import flask
import re
from flask import request
import yaml
import simplejson as json

from . import registry

dev = flask.Blueprint('swagger', __name__)

REST_METHODS = set(["POST", "GET", "PATCH", "PUT", "DELETE"])

@dev.route("/")
@registry.skip
def index():
    """Generate a swagger schema from all known routes."""
    definition = {
        "swagger": "2.0",
        "info": {
            "title": flask.config.get("APPNAME", "Not specified"),
            "version": flask.config.get("VERSION", "Not specified"),
        },
        "host": request.host,
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "definitions": registry._definitions,
        "paths": {}
    }

    rules = list(flask.current_app.url_map.iter_rules())
    for r in sorted(rules, key=operator.attrgetter('rule')):
        if r.rule.startswith('/static'):
            continue
        if r.endpoint in registry._skipped:
            continue

        rule = re.sub(r"<(?:[_a-zA-Z0-9\(\)]+:)?([a-zA-Z0-9_]+)>", r"{\1}", r.rule)
        if rule not in definition['paths']:
            definition['paths'][rule] = {}

        methods_handled = r.methods & REST_METHODS
        handler = flask.current_app.view_functions.get(r.endpoint)
        doc = handler.func_doc

        if len(methods_handled) == 1:
            method = methods_handled.pop().lower()
            try:
                validated = yaml.safe_load(doc)
                if not isinstance(validated, dict):
                    raise Exception("Not a descriptor")
                definition['paths'][rule][method] = validated
            except Exception:
                pass

        else:
            # We need to handle multi-method docstrings differently
            # because the documentation needs to define both, and
            # it's a higher level of the swagger hierarchy
            try:
                validated = yaml.safe_load(doc)
                if not isinstance(validated, dict):
                    raise Exception("Not a descriptor")
                definition['paths'][rule].update(validated)
            except Exception:
                definition['paths'][rule] = {}

    resp = flask.make_response(
            json.dumps(definition, for_json=True))
    resp.headers.set("Content-type", 'application/json')
    resp.headers.set("Access-Control-Allow-Origin", "*")
    return resp
