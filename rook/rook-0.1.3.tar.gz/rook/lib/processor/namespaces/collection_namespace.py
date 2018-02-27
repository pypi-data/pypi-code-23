import six

from .dumped_object_namespace import DumpedObjectNamespace

from .python_object_namespace import PythonObjectNamespace

from ...lib_interfaces import RookKeyNotFound


class CollectionNamespace(DumpedObjectNamespace):

    def __init__(self, original_size, type, common_type, attributes):
        super(CollectionNamespace, self).__init__(type, common_type, attributes, self.METHODS)
        self.original_size = original_size

    def read_key(self, key):
        try:
            return self[key]
        except KeyError:
            raise RookKeyNotFound(key)

    def size(self, args):
        return PythonObjectNamespace(len(self))

    def original_size(self, args):
        return PythonObjectNamespace(self.original_size)

    METHODS = (size, original_size)


class DictNamespace(CollectionNamespace, dict):

    def __init__(self, collection, original_size=None, collection_type=None, attributes={}):
        if not collection_type:
            collection_type = str(type(collection))

        if not original_size:
            original_size = len(collection)

        dict.__init__(self, collection)
        CollectionNamespace.__init__(self, original_size, collection_type, u'dict', attributes)

    def to_dict(self):
        items = [(key.to_dict(), value.to_dict()) for key, value in six.iteritems(self)]

        return {
            u'namespace': self.__class__.__name__,
            u'common_type': self.common_type,
            u'original_type': self.type,
            u'original_size': self.original_size,
            u'attributes': self.get_attributes_dict(),
            u'value': items
            }

    def to_simple_dict(self):
        items = {}
        for key, value in six.iteritems(self):
            items[key.obj] = value.to_simple_dict()

        return items


class ListNamespace(CollectionNamespace, list):

    def __init__(self, collection, original_size=None, collection_type=None, common_type=None, attributes={}):
        if not original_size:
            original_size = len(collection)

        if not collection_type:
            collection_type = str(type(collection))

        if not common_type:
            common_type = self.get_common_type(collection)

        list.__init__(self, collection)
        CollectionNamespace.__init__(self, original_size, collection_type, common_type, attributes)

    @staticmethod
    def get_common_type(collection):
        if isinstance(collection, list):
            return u'list'
        elif isinstance(collection, tuple):
            return u'tuple'
        elif isinstance(collection, (set, frozenset)):
            return u'set'
        else:
            return u'list_unknown'

    def __hash__(self):
        return hash(tuple(k for k in self))

    def to_dict(self):
        items = [item.to_dict() for item in self]

        return {
            u'namespace': self.__class__.__name__,
            u'common_type': self.common_type,
            u'original_type': self.type,
            u'original_size': self.original_size,
            u'attributes': self.get_attributes_dict(),
            u'value': items
            }

    def to_simple_dict(self):
        return [item.to_simple_dict() for item in self]
