# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Base definitions for Yams to JSON Schema mappers."""

import abc
from functools import wraps

import six

from cubicweb.appobject import AppObject

from .._compat import ABCMeta


__all__ = [
    'JSONSchemaMapper',
    'JSONSchemaDeserializer',
    'JSONSchemaSerializer',
]


def add_descriptive_metadata(schema, mapper):
    """Add "title" and "description" metadata to `schema` if found on
    `mapper`.
    """
    for keyword in ('title', 'description'):
        if keyword not in schema:
            value = getattr(mapper, keyword, None)
            if value is not None:
                schema[keyword] = value
    return schema


def add_links(schema_and_definitions):
    """Method decorator that collects Hyper-Schema links and possibly add them
    to JSON Schema produced by `schema_and_definitions` method.
    """
    @wraps(schema_and_definitions)
    def wrapper(self, schema_role=None):
        schema, defns = schema_and_definitions(self, schema_role=schema_role)
        if self.resource is not None and isinstance(schema, dict):
            links = [l.description_object(self.resource)
                     for l in self.links(schema_role=schema_role)]
            # Sort links to get predictable results.
            links.sort(key=lambda l: (l['href'], l.get('rel')))
            if links:
                schema['links'] = links
        return schema, defns

    return wrapper


class ProtectedDict(dict):
    """A dict which keys cannot be overridden."""

    def __setitem__(self, key, value):
        if key in self:
            raise ValueError("key '{}' is already defined".format(key))
        return super(ProtectedDict, self).__setitem__(key, value)


def object_schema(properties, required=None):
    schema = {
        'type': 'object',
        'properties': properties,
        'additionalProperties': False,
    }
    if required:
        schema['required'] = required
    return schema


@six.add_metaclass(abc.ABCMeta)
class JSONSchemaMapper(AppObject):
    """Abstract base class for mappers between Yams schema definitions and
    JSON Schema documents.
    """
    __registry__ = 'mappers'

    def __init__(self, _cw, resource=None, **extra):
        """Initialize a JSON Schema mapper from a CubicWeb `_cw` and a Pyramid
        `resource`.
        """
        self.resource = resource
        super(JSONSchemaMapper, self).__init__(_cw, **extra)

    def select_mapper(self, regid, **ctx):
        """Return a mapper with `regid` selected with `**ctx`.

        The `resource` bound to this mapper is passed in selection context,
        unless specified in `**ctx`.
        """
        ctx.setdefault('resource', self.resource)
        return self._cw.vreg['mappers'].select(regid, self._cw, **ctx)

    def json_schema(self, schema_role=None):
        """Return the JSON Schema for bound Yams context.

        If `schema_role` is not None a plain JSON Schema document is returned
        following specified *role* ("view", "creation" or "edition").
        Otherwise, a JSON Hyper Schema document with *links* is returned.
        """
        schema, definitions = self.schema_and_definitions(schema_role)
        if definitions:
            assert 'definitions' not in schema
            schema['definitions'] = definitions
        return schema

    @abc.abstractmethod
    @add_links
    def schema_and_definitions(self, schema_role):
        """Return the JSON (sub-)Schema for bound Yams context along with a
        dict of subschemas to be inserted in the main JSON Schema's
        "definitions" property.
        """

    def links(self, schema_role=None, **kwargs):
        """Yield Link appobjects matching regid and selection context of this
        mapper.

        Extra keyword arguments are used for Link appobjects selection (in
        addition to mapper's section context).
        """
        args = (self._cw, )
        kwargs.update(self.cw_extra_kwargs)
        links_registry = self._cw.vreg['links']
        for linkcls in links_registry.get(self.__regid__, ()):
            if linkcls.__select__(linkcls, *args, **kwargs) > 0:
                yield links_registry.selected(linkcls, args, kwargs)


@six.add_metaclass(ABCMeta)
class JSONSchemaDeserializer(object):
    """Abstract mixin class for mappers capable of deserializing a JSON
    `instance` valid under mapped JSON Schema and insert respective data into
    CubicWeb's database.
    """

    @abc.abstractmethod
    def values(self, instance):
        """Return a dict holding deserialized data from `instance` suitable for
        insertion in CubicWeb database for mapped schema element.

        Items from `instance` dictionnary are pop-ed upon processing.
        """

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is JSONSchemaDeserializer:
            if any('values' in parent.__dict__
                   for parent in subclass.__mro__):
                return True
        return NotImplemented


@six.add_metaclass(ABCMeta)
class JSONSchemaSerializer(object):
    """Abstract mixin class for mappers capable of serializing data from
    CubicWeb's database as a JSON `instance` valid under mapped JSON Schema.
    """

    @abc.abstractmethod
    def serialize(self, *args):
        """Return the serialized value for mapped schema element."""

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is JSONSchemaSerializer:
            if any('serialize' in parent.__dict__
                   for parent in subclass.__mro__):
                return True
        return NotImplemented
