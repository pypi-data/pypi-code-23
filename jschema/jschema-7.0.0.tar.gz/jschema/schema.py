import os
import io
import subprocess

import yaml
import json

from .node import RootNode
from .errors import JrsSchemaError


class Schema(object):

    def __init__(self):
        self._schemas_dirs = {}
        self._schemas = {}
        self._nodes = {}

    @property
    def schemas_dirs(self):
        return self._schemas_dirs

    @property
    def schemas(self):
        return self._schemas

    @property
    def nodes(self):
        return self._nodes

    def get(self, name):
        if name not in self._schemas:
            raise JrsSchemaError("Schema not found: {}".format(name))

        return self._schemas[name]

    def load(self, root):
        res = subprocess.check_output(["find", root, "-name", "*.yaml"])
        for fpath in res.split():
            with io.open(fpath, encoding="utf-8") as fstream:
                schema = yaml.load(fstream)

            if "id" not in schema:
                raise JrsSchemaError(u"Attribute 'id' not exists: {}".format(fpath))
            if "type" not in schema:
                raise JrsSchemaError(u"Attribute 'type' not exists: {}".format(fpath))
            if schema["type"] == "method" and "params" not in schema:
                raise JrsSchemaError(u"Attribute 'params' not exists in method: {}".format(fpath))

            self._schemas[schema["id"]] = schema
            self._schemas_dirs[schema["id"]] = os.path.dirname(fpath).decode("utf-8").replace(root, "", 1).lstrip("/")

    def resolve_refs(self):
        RootNode.set_schemas(self._schemas)
        for key in self._schemas:
            schema_node = RootNode(key)
            schema_node.find_refs()
            schema_node.replace_refs()
            self._nodes[key] = schema_node

    def clear(self):
        for schema in self._schemas.values():
            RootNode.clear(schema)

    def toJson(self, prettyPrint=False):
        if prettyPrint:
            return json.dumps(self._schemas, separators=(',', ': '), indent=4)
        else:
            return json.dumps(self._schemas, separators=(',', ':'))
