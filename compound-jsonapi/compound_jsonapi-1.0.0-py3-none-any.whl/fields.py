"""
:mod:`compound_jsonapi.fields`
==============================

Provides the :class:`~compound_jsonapi.fields.Relationship` custom field for
defining relationships between :class:`~compound_jsonapi.schema.Schema`\ s.

.. moduleauthor:: Mark Hall <mark.hall@work.room3b.eu>
"""
import marshmallow as ma

_RECURSIVE_NESTED = 'self'


class Relationship(ma.fields.Field):
    """The :class:`~compound_jsonapi.fields.Relationship` creates a link between
    two :class:`~compound_jsonapi.schema.Schema`. The linked
    :class:`~compound_jsonapi.schema.Schema` can either be provided as a class
    or a dotted classname string.
    """

    def __init__(self, schema, many=False, **kwargs):
        """
        :param schema: The :class:`~compound_jsonapi.schema.Schema` that defines
                       how to handle the linked data.
        :param many: By default the relationship is one-to-one. Set this to
                     ``true`` to create a one-to-many relationship
        :type many: ``bool``
        """
        super(Relationship, self).__init__(**kwargs)
        self.many = many
        self.__schema = schema

    @property
    def schema(self):
        """Property that returns an instantiated :class:`~compound_jsonapi.schema.Schema`
        for the relationship."""
        if isinstance(self.__schema, ma.base.SchemaABC):
            pass
        elif isinstance(self.__schema, type) and issubclass(self.__schema, ma.base.SchemaABC):
            self.__schema = self.__schema()
        elif isinstance(self.__schema, ma.compat.basestring):
            if self.__schema == _RECURSIVE_NESTED:
                parent_class = self.parent.__class__
                self.__schema = parent_class()
            else:
                schema_class = ma.class_registry.get_class(self.__schema)
                self.__schema = schema_class()
        self.__schema._visited = self.root._visited
        self.__schema._included_data = self.root._included_data
        self.__schema.include_schemas = self.root.include_schemas
        self.__schema._parent = self.root
        return self.__schema

    def _deserialize(self, value, attr=None, data=None):
        """Deserialise the given ``value``. Returns a tuple ``(type, id)``
        if the relationship is one-to-one otherwise retursn a ``list`` of
        such tuples."""
        if self.many:
            return [(v['type'], v['id']) for v in value]
        else:
            return (value['type'], value['id'])

    def _serialize(self, value, attr=None, data=None):
        """Serialises the given ``value``. Will only serialise if the relationship's
        :class:`~compound_jsonapi.schema.Schema` is included in the list of
        :class:`~compound_jsonapi.schema.Schema`\ s that have been set in the
        ``include_schemas`` parameter when creating the root
        :class:`~compound_jsonapi.schema.Schema`. Uses the ``_visited`` property
        of the :func:`~compound_jsonapi.schema.Schema.schema` to correctly handle
        circular relationship structures."""
        if self.schema.Meta.type_ in self.schema.include_schemas and value is not None:
            visited = getattr(self.schema, '_visited')
            included_data = getattr(self.schema, '_included_data')
            if self.many:
                result = []
                for part in value:
                    if (self.schema.Meta.type_, str(self.schema.get_attribute(part, 'id', None))) not in visited:
                        visited.append((self.schema.Meta.type_, str(self.schema.get_attribute(part, 'id', None))))
                        included, errors = self.schema.dump(part, many=False)
                        included_data[(self.schema.Meta.type_,
                                       str(self.schema.get_attribute(part, 'id', None)))] = included['data']
                    result.append({'type': self.schema.Meta.type_,
                                   'id': str(self.schema.get_attribute(part, 'id', None))})
                return result
            else:
                if (self.schema.Meta.type_, str(self.schema.get_attribute(value, 'id', None))) not in visited:
                    visited.append((self.schema.Meta.type_, str(self.schema.get_attribute(value, 'id', None))))
                    included, errors = self.schema.dump(value, many=False)
                    included_data[(self.schema.Meta.type_,
                                   str(self.schema.get_attribute(value, 'id', None)))] = included['data']
                return {'type': self.schema.Meta.type_, 'id': str(self.schema.get_attribute(value, 'id', None))}
        else:
            if self.many:
                return []
            else:
                return None
