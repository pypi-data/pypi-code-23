from .node import Node


class RootNode(Node):

    _schemas = {}

    @classmethod
    def set_schemas(cls, schemas):
        cls._schemas = schemas

    @property
    def ns(self):
        return self._ns

    @property
    def refs(self):
        return self._refs

    @property
    def value(self):
        return RootNode._schemas[self._key]

    @value.setter
    def value(self, new_value):
        raise Exception("RootNode.value read only")

    def __init__(self, key):
        self._key = key
        self._parent = None
        self._root = self
        self._childs = []
        self._path = []
        self._refs = []

        self._ns = None
        split = key.split(".")
        if len(split) == 2:
            self._ns = split[0]

    def add_ref(self, ref):
        self._refs.append(ref)
