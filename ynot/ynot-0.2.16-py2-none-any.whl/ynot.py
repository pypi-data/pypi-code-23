from __future__ import print_function, unicode_literals

import sys
import io
import re
import json
import string
from collections import OrderedDict
from copy import copy
from . import *

import yaml
import jsonschema
import jsonpath_ng.ext as jsonpath

from constants import *
from templateresolver import resolve_template
import pathresolver

class VerificationException(Exception):
    pass

class Node:
    def __init__(self, data, variables={}):
        self.data = data
        self.variables = variables
    @classmethod
    def from_yaml(cls, yamldata):
        return cls(yaml.load(yamldata))

class Transformation:
    def __init__(self, document, trafo, write=sys.stdout.write):
        self.document = document
        self.trafo = trafo
        self.nodes = [document]
        self.variables = dict({"depth": len(self.nodes)}, **trafo.variables)
        self.paths = ['$']
        self.write = write
        logger.debug("document: %s" % (document.data))
    def transform(self):
        self._process_actions(self.trafo.actions, self.paths[-1], self.nodes[-1].data)
    def _exec_log(self, **kwargs):
        argmap = {'path': self.paths[-1], 'pathstack': self.paths, 'node': self.nodes[-1].data, 'document': self.document.data}
        logger.info(kwargs.get("value").format(**argmap))
    def _exec_print(self, **kwargs):
        self.write(self._get_expanded(kwargs.get("value")) + '\n')
    def _exec_write(self, **kwargs):
        self.write(self._get_expanded(kwargs.get("value")))
    def _exec_print_map(self, **kwargs):
        self.write(yaml.safe_dump(self._get_expanded(kwargs), **yaml_defaults) + '\n')
    def _exec_for(self, **kwargs):
        actions = kwargs.get("actions", [])
        path = pathresolver.resolve(kwargs["path"], self.paths[-1])
        matches = Transformation.get_matches(path, self.document.data)
        logger.debug("exec_for: {path: %s, actions: %s}" % (path, actions))
        for match in matches:
            self.nodes.append(Node(match.value))
            self.paths.append(stringtype("%s" % match.full_path))
            self.variables.update({"_depth": len(self.nodes)})
            self._process_actions(actions, self.paths[-1], match.value)
            self.paths.pop()
            self.nodes.pop()
    def _exec_call(self, **kwargs):
        self._process_actions(self.trafo.routines[kwargs["value"]], self.paths[-1], self.nodes[-1].data)
    def _exec_set(self, **kwargs):
        for key, value in kwargs.iteritems():
            self.nodes[-1].variables[key] = value
    def _exec_eval(self, **kwargs):
        eval(kwargs["value"])
    def _exec_exec(self, **kwargs):
        exec(kwargs["value"])
    def _get_action_str(self, action):
        try:
            if isinstance(action.values()[0], basestring):
                action[action.keys()[0]] = {'value': action.values()[0]}
            elif action.values()[0] is not None and not isinstance(action.values()[0], dict):
                logger.error("type(action.values()[0]): %s" % (type(action.values()[0])), exc_info=True)
                raise Exception("unexpected value type")
        except Exception, e:
            logger.error("\n\taction: \n%s" % (yaml.safe_dump(action)), exc_info=True)
        return "self._exec_%s(**%s)" % (action.keys()[0], {k: v for k, v in action.values()[0].iteritems()} if action.values()[0] is not None else {})
    def _process_actions(self, actions, path, matchvalue):
        for action in actions:
            logger.debug("process_action: {action: %s, path: %s, match: %s}" % (action, path, matchvalue))
            try:
                eval(self._get_action_str(action))
            except Exception, e:
                logger.error("\n\tpath: %s\n\taction: \n%s\n\tmatch: \n%s" % (path, yaml.safe_dump(action), yaml.safe_dump(matchvalue)), exc_info=True)
    def _get_variables(self):
        node = dict(self.nodes[-1].data) if isinstance(self.nodes[-1].data, dict) else {}
        return dict(node, **dict(self.trafo.constants, **dict(self.variables, **self.nodes[-1].variables)))
    def _get_data(self):
        data = self.nodes[-1].data
        if isinstance(data, dict) or isinstance(data, list):
            data = yaml.dump(data, **yaml_defaults)
        else:
            data = stringtype(data)
        return data
    def _get_expanded(self, value):
        if value is not None:
            if isinstance(value, basestring):
                #expanded_path = resolve_template(value, self.document.data, self.paths[-1])
                #expanded_variables = string.Template(expanded_path).safe_substitute(self._get_variables())
                #return expanded_variables
                #TODO: Decide which one is better ...
                expanded_variables = string.Template(value).safe_substitute(self._get_variables())
                expanded_path = resolve_template(expanded_variables, self.document.data, self.paths[-1])
                return expanded_path
            elif isinstance(value, dict):
                for k, v in value.iteritems():
                    expanded = self._get_expanded(v)
                    try:
                        return {k: yaml.load(expanded)}
                    except Exception:
                        return {k: expanded}
            elif isinstance(value, list):
                for v in value:
                    return yaml.load(self._get_expanded(v))
            else:
                raise Exception("Unexpected type '%s'" % (type(value)))
        else:
            return self._get_expanded(self._get_data())
    @staticmethod
    def get_matches(path, node):
        try:
            return jsonpath.parse(path).find(node)
        except Exception, e:
            logger.error("\n\tpath: %s" % (path), exc_info=True)

class Trafo:
    def __init__(self, id="<undefined>", actions=[], routines={}, samples={}, constants={}, variables={}, **kwargs):
        self.id = id
        self.actions = actions
        self.routines = routines
        self.samples = samples
        self.constants = constants
        self.variables = variables
        if kwargs.get("verify"):
            self.verify()
    def verify(self):
        for key, sample in self.samples.iteritems():
            document = Node(sample["input"])
            output = io.StringIO()
            Transformation(document, self, write=output.write).transform()
            result = output.getvalue()
            expected = sample.get("output")
            if (expected and result != expected):
                logger.error(verificationmessage % {
                    "id": key,
                    "expected": sample["output"],
                    "result": result}, exc_info=True)
                raise VerificationException("Verifying sample %s failed for trafo %s" % (key, self.id))
            if not expected:
                print(output.getvalue())
    @classmethod
    def from_dict(cls, data, trafoschema, verify=True):
        trafo = data
        try:
            jsonschema.validate(trafo, yaml.safe_load(trafoschema))
        except jsonschema.exceptions.ValidationError, e:
            logger.error(validationmessage % {
                "message": e.message,
                "docpath": list(e.absolute_path),
                "schemapath": list(e.absolute_schema_path)}, exc_info=True)
            raise Exception("Schema validation failed for trafo %s" % (trafo.get("id", "<unknown>")))
        return cls(verify=verify, **trafo)

    @classmethod
    def from_yaml(cls, yamldata, trafoschema, verify=True):
        return cls.from_dict(yaml.load(yamldata), trafoschema, verify=True)
