from __future__ import print_function, unicode_literals

import sys
import io
import re
import json
import string
from collections import OrderedDict

import yaml
import jsonschema
import jsonpath_ng.ext as jsonpath

from globals import *
from templateresolver import resolve_template
from trafoschema import trafoschema

def orderedDict_constructor(loader, node, deep=False):
    data = OrderedDict()
    yield data
    if isinstance(node, yaml.MappingNode):
        loader.flatten_mapping(node)
    data.update(OrderedDict(loader.construct_pairs(node, deep)))

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, orderedDict_constructor)
yaml.add_constructor(u'tag:yaml.org,2002:timestamp', yaml.constructor.SafeConstructor.construct_yaml_str)
yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_dict(data.iteritems()))

class VerificationException(Exception):
    pass

class Node:
    def __init__(self, data):
        self.data = data
        self.variables = {}
    @classmethod
    def from_yaml(cls, yamldata):
        return cls(yaml.load(yamldata))

class Transformation:
    def __init__(self, document, trafo, write=sys.stdout.write):
        self.document = document
        self.trafo = trafo
        self.node = [document]
        self.variables = trafo.variables
        self.path = ['$']
        self.write = write
        logger.debug("document: %s" % (document.data))
    def transform(self):
        self._process_actions(self.trafo.actions, self.path[-1], self.node[-1].data)
    def _exec_print(self, **kwargs):
        self._write(kwargs.get("value"), '\n')
    def _exec_write(self, **kwargs):
        self._write(kwargs.get("value"))
    def _exec_for(self, **kwargs):
        actions = kwargs.get("actions", [])
        relpath = kwargs["path"]
        path = self.path[-1] + relpath if relpath[0] != '$' else relpath
        matches = Trafo.get_matches(path, self.document.data)
        logger.debug("exec_for: {path: %s, actions: %s}" % (path, actions))
        for match in matches:
            self.node.append(Node(match.value))
            self.path.append(stringtype("$.%s" % match.full_path))
            self._process_actions(actions, self.path[-1], match.value)
            self.path.pop()
    def _exec_call(self, **kwargs):
        for action in self.trafo.routines[kwargs["value"]]:
            eval(self._get_action_str(action))
    def _exec_set(self, **kwargs):
        for key, value in kwargs.iteritems():
            self.variables[key] = value
    def _exec_eval(self, **kwargs):
        self.variables[kwargs.get("target")] = eval(kwargs["value"])
        return eval(kwargs["value"])
    def _exec_exec(self, **kwargs):
        exec(kwargs["value"])
    def _get_action_str(self, action):
        try:
            if isinstance(action.values()[0], stringtype):
                action[action.keys()[0]] = {'value': action.values()[0]}
            return "self._exec_%s(**%s)" % (action.keys()[0], {k: v for k, v in action.values()[0].iteritems()} if action.values()[0] is not None else {})
        except Exception, e:
            logger.error("\n\taction: %s" % (action), exc_info=True)
    def _process_actions(self, actions, path, matchvalue):
        for action in actions:
            logger.debug("process_action: {action: %s, path: %s, match: %s}" % (action, path, matchvalue))
            try:
                eval(self._get_action_str(action))
            except Exception, e:
                logger.error("\n\tpath: %s\n\taction: %s\n\tmatch: %s" % (path, action, matchvalue), exc_info=True)
    def _get_variables(self):
        node = dict(self.node[-1].data) if isinstance(self.node[-1].data, dict) else {}
        return dict(node, **dict(self.trafo.constants, **self.variables))
    def _write(self, value, end=""):
        expanded_path = resolve_template(value, self.document.data, self.path[-1])
        if value is not None:
            self.write(string.Template(expanded_path).substitute(self._get_variables()) + end)
        else:
            self.write(stringtype(self.node[-1].data) + end)

class Trafo:
    def __init__(self, id="<undefined>", actions=[], routines={}, samples=[], constants={}, variables={}):
        self.id = id
        self.actions = actions
        self.routines = routines
        self.samples = samples
        self.constants = constants
        self.variables = variables
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
                    "result": result})
                raise VerificationException("Verifying sample %s failed for trafo %s" % (key, self.id))
            if not expected:
                print(output.getvalue())
    @classmethod
    def from_yaml(cls, yamldata):
        trafo = yaml.load(yamldata)
        try:
            jsonschema.validate(trafo, yaml.load(trafoschema))
        except jsonschema.exceptions.ValidationError, e:
            logger.error(validationmessage % {
                "message": e.message,
                "docpath": list(e.absolute_path),
                "schemapath": list(e.absolute_schema_path)})
            raise Exception("Schema validation failed for trafo %s" % (trafo.get("id", "<unknown>")))
        return cls(**trafo)
    @staticmethod
    def get_matches(path, node):
        try:
            return jsonpath.parse(path).find(node)
        except Exception, e:
            logger.error("\n\tpath: %s\n\tnode: %s" % (path, node), exc_info=True)
