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
"""Appobjects for mapping Yams schema definitions to JSON Schema documents."""

from six import text_type

from logilab.common.registry import yes
from cubicweb import (
    _,
    neg_role,
    Unauthorized,
    ValidationError,
)
from cubicweb.predicates import (
    match_kwargs,
)

from cubicweb_jsonschema import (
    CREATION_ROLE,
    EDITION_ROLE,
    VIEW_ROLE,
)

from .base import (
    JSONSchemaMapper,
    JSONSchemaDeserializer,
    JSONSchemaSerializer,
    ProtectedDict,
    add_descriptive_metadata,
    add_links,
    object_schema,
)
from .predicates import (
    yams_component_target,
)


__all__ = [
    'ETypeMapper',
    'TargetETypeMapper',
    'EntityMapper',
    'TargetEntityMapper',
    'EntityCollectionMapper',
    'RelatedCollectionMapper',
    'CollectionItemMapper',
]


@JSONSchemaDeserializer.register
class ETypeMapper(JSONSchemaMapper):
    """JSON Schema mapper for entity types."""
    __regid__ = 'jsonschema.entity'
    __select__ = match_kwargs('etype')

    @property
    def etype(self):
        return self.cw_extra_kwargs['etype']

    @property
    def entity(self):
        """Entity bound to this mapper, None for ETypeMapper."""
        return None

    @property
    def title(self):
        return self._cw._(self.etype)

    @add_links
    def schema_and_definitions(self, schema_role=None):
        properties = {}
        required = []
        definitions = ProtectedDict()

        def insert_property(name, subschema, defs, mapper):
            if subschema is None:
                return
            properties[name] = subschema
            if defs:
                definitions.update(defs)
            if mapper.required(schema_role):
                required.append(name)

        for mapper in self._object_mappers():
            subschema, defs = mapper.schema_and_definitions(schema_role)
            insert_property(mapper.name, subschema, defs, mapper)

        for rtype, role, target_types in self.relations(schema_role):
            if target_types is None:
                target_types = self._rtype_target_types(rtype, role)
            assert isinstance(target_types, set), target_types
            mapper = self._relation_mapper(rtype, role, target_types)
            subschema, defs = mapper.schema_and_definitions(schema_role)
            insert_property(rtype, subschema, defs, mapper)

        schema = object_schema(properties, required)
        return add_descriptive_metadata(schema, self), definitions

    def links(self, schema_role=None):
        """Yield Link appobjects matching regid and selection context of this
        entity mapper along with selectable "jsonschema.relation" links for
        "subject" relations.
        """
        if schema_role is not None:
            return
        for linkcls in super(ETypeMapper, self).links():
            yield linkcls
        links_registry = self._cw.vreg['links']
        for rtype, role, __ in self.relations(VIEW_ROLE, section='related'):
            if role != 'subject':
                continue
            yield links_registry.select(
                'jsonschema.relation', self._cw,
                entity=self.entity, rtype=rtype, role=role,
            )

    def values(self, instance):
        """Return a dict with deserialized data from `instance` suitable for
        insertion in CubicWeb database.
        """
        entity = self.entity
        values = {}
        # Deserialize "jsonschema.object" mappers first.
        for mapper in self._object_mappers():
            values.update(mapper.values(entity, instance))
        # Then Yams relations.
        if entity is None:
            schema_role = CREATION_ROLE
        else:
            schema_role = EDITION_ROLE
        for rtype, role, target_types in self.relations(schema_role):
            mapper = self._relation_mapper(rtype, role, target_types)
            values.update(mapper.values(entity, instance))
        if instance:
            # All properties in "instance" should have been consumed at this
            # point.
            eid = entity.eid if entity is not None else None
            msg = _('unexpected properties: {}').format(', '.join(instance))
            raise ValidationError(eid, {None: msg})
        return values

    def relations(self, schema_role, section='inlined'):
        """Yield relation information tuple (rtype, role, targettypes)
        for given schema role in the context of bound entity type.

        Keyword argument `section` controls uicfg section to select relations
        in.
        """
        try:
            permission = {
                None: 'read',
                VIEW_ROLE: 'read',
                CREATION_ROLE: 'add',
                EDITION_ROLE: 'update',
            }[schema_role]
        except KeyError:
            raise ValueError('unhandled schema role "{0}" in {1}'.format(
                schema_role, self))
        entity = self.entity
        if entity is None:
            entity = self._cw.vreg['etypes'].etype_class(self.etype)(self._cw)
        rsection = self._cw.vreg['uicfg'].select(
            'jsonschema', self._cw, entity=entity)
        return rsection.relations_by_section(entity, section, permission)

    def _object_mappers(self):
        """Yield 'jsonschema.object' mapper instance selectable for entity
        bound to this mapper.
        """
        if 'jsonschema.object' not in self._cw.vreg['mappers']:
            return
        for mappercls in self._cw.vreg['mappers']['jsonschema.object']:
            if mappercls.__select__(mappercls, self._cw, etype=self.etype) > 0:
                yield mappercls(self._cw)

    def _rtype_target_types(self, rtype, role):
        rschema = self._cw.vreg.schema[rtype]
        return {t.type for t in rschema.targets(self.etype, role)}

    def _relation_mapper(self, rtype, role, target_types=None):
        return self.select_mapper(
            'jsonschema.relation',
            etype=self.etype, rtype=rtype, role=role, target_types=target_types)


class TargetETypeMapper(ETypeMapper):
    """Specialized version of :class:`ETypeMapper` selectable for an entity
    type as target of (`rtype`, `role`) relation.
    """
    __select__ = match_kwargs('etype', 'rtype', 'role')

    @property
    def rtype(self):
        return self.cw_extra_kwargs['rtype']

    @property
    def role(self):
        return self.cw_extra_kwargs['role']

    def relations(self, schema_role, section='inlined'):
        relations = super(TargetETypeMapper, self).relations(
            schema_role, section=section)
        for rtype, role, target_types in relations:
            if (rtype, role) == (self.rtype, self.role):
                continue
            yield rtype, role, target_types


@JSONSchemaSerializer.register
class EntityMapper(ETypeMapper):
    """JSON Schema mapper for an entity."""
    __select__ = match_kwargs('entity')

    @property
    def entity(self):
        """Live entity from selection context."""
        return self.cw_extra_kwargs['entity']

    @property
    def etype(self):
        return self.entity.cw_etype

    def _relation_mapper(self, rtype, role, target_types=None):
        return self.select_mapper(
            'jsonschema.relation',
            entity=self.entity, rtype=rtype,
            role=role, target_types=target_types,
            resource=None,
        )

    def serialize(self):
        """Return the serialized value entity bound to this mapper."""
        entity = self.entity
        entity.complete()
        data = {}
        for mapper in self._object_mappers():
            data[mapper.name] = mapper.serialize(entity)
        for rtype, role, target_types in self.relations(VIEW_ROLE):
            relation_mapper = self._relation_mapper(rtype, role, target_types)
            value = relation_mapper.serialize(entity)
            if value is None:
                continue
            data[relation_mapper.orm_rtype] = value
        return data


class TargetEntityMapper(EntityMapper, TargetETypeMapper):
    """Specialized version of :class:`TargetETypeMapper` and
    :class:`EntityMapper` selectable for an *entity* as target of (`rtype`,
    `role`) relation.
    """
    __select__ = match_kwargs('entity', 'rtype', 'role')


@JSONSchemaDeserializer.register
@JSONSchemaSerializer.register
class EntityCollectionMapper(JSONSchemaMapper):
    """Mapper for a collection of entities."""
    __regid__ = 'jsonschema.collection'
    __select__ = match_kwargs('etype')

    def __repr__(self):
        return '<{0.__class__.__name__} etype={0.etype}'.format(self)

    @property
    def etype(self):
        return self.cw_extra_kwargs['etype']

    @property
    def title(self):
        """Title of the collection, plural form of entity type."""
        return self._cw._('{}_plural').format(self.etype)

    @add_links
    def schema_and_definitions(self, schema_role=None):
        if schema_role == CREATION_ROLE:
            return self._submission_schema_and_definitions()
        return self._array_schema(schema_role=schema_role)

    def _submission_schema_and_definitions(self):
        """Delegate generation of schema and definitions to the "entity"
        mapper corresponding to the entity type in this collection.
        """
        mapper = self.select_mapper(
            'jsonschema.entity', **self.cw_extra_kwargs)
        return mapper.schema_and_definitions(schema_role=CREATION_ROLE)

    def _array_schema(self, schema_role=None):
        item_mapper = self.select_mapper(
            'jsonschema.item', **self.cw_extra_kwargs)
        items_schema, items_defs = item_mapper.schema_and_definitions(
            schema_role)
        schema = {
            'type': 'array',
            'items': items_schema,
        }
        return add_descriptive_metadata(schema, self), items_defs

    def links(self, schema_role=None):
        """Yield Link appobjects matching regid and selection context of this
        mapper if schema_role is None.
        """
        if schema_role is not None:
            return
        for link in super(EntityCollectionMapper, self).links(
                schema_role=schema_role):
            yield link

    def values(self, instance):
        mapper = self.select_mapper(
            'jsonschema.entity', **self.cw_extra_kwargs)
        return mapper.values(instance)

    def serialize(self, entities):
        """Return a list of collection item representing each entity in
        `entities`.
        """
        mapper = self.select_mapper('jsonschema.item', **self.cw_extra_kwargs)
        return [mapper.serialize(entity) for entity in entities]


class RelatedCollectionMapper(EntityCollectionMapper):
    """Mapper for a collection of entities through an *inlined* relation."""
    __select__ = (
        match_kwargs('entity', 'rtype', 'role')
        & yams_component_target()
    )

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                ' rtype={0.rtype} role={0.role}>'.format(self))

    @property
    def role(self):
        return self.cw_extra_kwargs['role']

    @property
    def rtype(self):
        return self.cw_extra_kwargs['rtype']

    @property
    def title(self):
        """Title of the collection, name of the relation."""
        return self._cw._(self.rtype if self.role == 'subject'
                          else self.rtype + '-object')

    def _submission_schema_and_definitions(self):
        """Delegate generation of schema and definitions to the "entity"
        mapper selected with possible target of `rtype`, `role` bound to this
        mapper.
        """
        rschema = self._cw.vreg.schema[self.rtype]
        target_types = rschema.targets(role=self.role)
        assert len(target_types) == 1, \
            'cannot handle multiple target types in {}'.format(self)
        target_type = target_types[0]
        entity = self.cw_extra_kwargs['entity']
        mapper = self.select_mapper(
            'jsonschema.entity', etype=target_type,
            rtype=self.rtype, role=neg_role(self.role),
            target_types={entity.cw_etype},
        )
        return mapper.schema_and_definitions(schema_role=CREATION_ROLE)


class NonInlinedRelatedCollectionMapper(RelatedCollectionMapper):
    """Mapper for a collection of entities through a non-*inlined* relation."""
    __select__ = (
        match_kwargs('entity', 'rtype', 'role')
        & ~yams_component_target()
    )

    def _submission_schema_and_definitions(self):
        """Return schema and definitions accounting for constraints on
        possible targets of `rtype`, `role` relation information for `entity`
        bound to this mapper.
        """
        entity = self.cw_extra_kwargs['entity']
        rschema = self._cw.vreg.schema[self.rtype]
        # XXX similar loop in ETypeRelationItemMapper.relation_targets().
        ids = []
        for target_type in rschema.targets(role=self.role):
            try:
                rset = entity.unrelated(
                    self.rtype, target_type, role=self.role)
            except Unauthorized:
                continue
            for target in rset.entities():
                ids.append({
                    'type': 'string',
                    'enum': [text_type(target.eid)],
                    'title': target.dc_title(),
                })
        if not ids:
            return False, None
        properties = {
            'id': {
                'oneOf': ids,
            },
        }
        schema = object_schema(properties, required=['id'])
        return add_descriptive_metadata(schema, self), None


@JSONSchemaSerializer.register
class CollectionItemMapper(JSONSchemaMapper):
    """Mapper for an item of a collection."""
    __regid__ = 'jsonschema.item'
    __select__ = yes()

    @add_links
    def schema_and_definitions(self, schema_role=None):
        """Return either a string schema or an object with "type", "id and
        "title" properties.
        """
        if schema_role == CREATION_ROLE:
            schema = {
                'type': 'string',
            }
        else:
            schema = {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                    },
                    'id': {
                        'type': 'string',
                    },
                    'title': {
                        'type': 'string',
                    },
                },
            }
        return add_descriptive_metadata(schema, self), {}

    def links(self, schema_role=None, **kwargs):
        kwargs['anchor'] = '#'
        return super(CollectionItemMapper, self).links(
            schema_role=schema_role, **kwargs)

    @staticmethod
    def serialize(entity):
        """Return a dictionary with entity represented as a collection item."""
        return {
            'type': entity.cw_etype.lower(),
            'id': text_type(entity.eid),
            'title': entity.dc_title(),
        }
