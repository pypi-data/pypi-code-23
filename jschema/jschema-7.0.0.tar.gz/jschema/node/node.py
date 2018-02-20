from copy import deepcopy
from ..errors import JrsNodeError


class Node(object):

    @classmethod
    def set_schemas(cls, schemas):
        cls._schemas = schemas

    @staticmethod
    def clear(schema, parent_key=None):
        if parent_key == "properties":
            return

        value_type = type(schema)
        if value_type == dict:
            schema.pop("title", None)
            schema.pop("description", None)

            for key, value in schema.items():
                Node.clear(value, key)
        elif value_type == list:
            for i, value in enumerate(schema):
                Node.clear(value, i)

    def __init__(self, key, parent, root, path):
        self._key = key
        self._parent = parent
        self._root = root
        self._childs = []
        self._path = path[:]
        self._path.append(key)

    @property
    def key(self):
        return self._key

    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        return self._root

    @property
    def path(self):
        return self._path

    @property
    def value(self):
        return self._parent.value[self._key]

    @value.setter
    def value(self, new_value):
        self._parent.value[self._key] = new_value

    def _store_ref(self):
        ref = self.value["$ref"]

        if ref.index("#") == 0:
            self._root.add_ref({
                "node": self,
                "type": "local",
                "path": ref[1:],
                "context": self._root.value,
                "origin_value": deepcopy(self.value),
                "value": ref,
            })
        else:
            schemaId, path = ref.split("#")
            if schemaId not in self._root._schemas:
                raise JrsNodeError(JrsNodeError.make_message(u"Schema '{}' not exists".format(schemaId), self))
            self._root.add_ref({
                "node": self,
                "type": "global",
                "path": path,
                "context": self._root._schemas[schemaId],
                "origin_value": deepcopy(self.value),
                "value": ref
            })

    def find_refs(self):
        value_type = type(self.value)
        is_ref = value_type is dict and "$ref" in self.value
        is_dict = value_type is dict
        is_list = value_type is list

        if is_ref:
            self._store_ref()
        elif is_dict:
            self._childs = [
                Node(key, parent=self, root=self._root, path=self._path)
                for key in self.value
            ]
        elif is_list:
            self._childs = [
                Node(index, parent=self, root=self._root, path=self._path)
                for index in range(len(self.value))
            ]

        if self._childs:
            for child in self._childs:
                child.find_refs()

    def replace_refs(self):
        for item in self._refs:
            node = item["node"]

            value = item["context"]
            if item["path"]:
                for key in item["path"].strip("/").split("/"):
                    if key in value:
                        value = value[key]
                    else:
                        raise JrsNodeError(JrsNodeError.make_message(u"Can't resolve ref path", node))

            node.value = value

        for item in self._refs:
            node = item["node"]
            node_value = deepcopy(node.value)

            for key, value in item["origin_value"].items():
                if key == "$ref":
                    continue
                node_value[key] = value

            node.value = node_value
