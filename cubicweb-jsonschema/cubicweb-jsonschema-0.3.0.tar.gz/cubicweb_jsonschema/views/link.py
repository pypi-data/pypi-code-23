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

"""cubicweb-jsonschema hyper schema "link" components.

See http://json-schema.org/draft-06/links for the JSON schema of these
objects.
"""


from cubicweb.appobject import AppObject
from cubicweb.predicates import (
    has_permission,
    match_kwargs,
    score_entity,
)

from .. import VIEW_ROLE, CREATION_ROLE, EDITION_ROLE


def tag_uri(date, name):
    assert isinstance(date, (int, str))
    return 'tag:cubicweb.org,{}:{}'.format(date, name)


class Link(AppObject):
    """Abstract hyper schema link."""
    __registry__ = 'links'

    def description_object(self, resource):
        """Return the link description object as a dict."""
        raise NotImplementedError()


class CollectionLink(Link):
    """Link for a collection."""
    __regid__ = 'jsonschema.collection'
    __select__ = match_kwargs('title')
    rel = 'collection'

    @property
    def title(self):
        return self.cw_extra_kwargs['title']

    def description_object(self, resource):
        request = resource.request
        return {
            u'href': request.resource_path(resource),
            u'rel': self.rel,
            u'targetSchema': {
                u'$ref': request.resource_path(resource, 'schema'),
            },
            u'submissionSchema': {
                u'$ref': request.resource_path(resource, 'schema',
                                               query={'role': CREATION_ROLE}),
            },
            u'title': self.title,
        }


class CollectionItemLink(Link):
    """Link for a collection item."""
    __regid__ = 'jsonschema.item'
    __select__ = match_kwargs('anchor')
    rel = 'item'

    def description_object(self, resource):
        request = resource.request
        href = request.resource_path(resource) + '{id}'
        return {
            u'href': href,
            u'rel': self.rel,
            u'anchor': self.cw_extra_kwargs['anchor'],
        }


class ETypeLink(CollectionLink):
    """Link for a collection of entities of the same type."""
    __regid__ = 'jsonschema.collection'
    __select__ = match_kwargs('etype')
    rel = 'self'

    @property
    def title(self):
        etype = self.cw_extra_kwargs['etype']
        return self._cw.__(etype + '_plural')


class EntityLink(Link):
    """Abstract hyper schema link suitable for entity JSON schema."""
    __abstract__ = True
    __regid__ = 'jsonschema.entity'
    __select__ = match_kwargs('entity')

    @property
    def entity(self):
        return self.cw_extra_kwargs['entity']


class EntitySelfLink(EntityLink):
    """Link for an entity as rel="self"."""
    __select__ = EntityLink.__select__ & has_permission('read')

    def description_object(self, resource):
        request = resource.request
        entity = self.entity
        title = self._cw._('{0} #{1}').format(
            self._cw.__(entity.cw_etype), entity.eid)
        return {
            u'href': request.resource_path(resource),
            u'rel': u'self',
            u'title': title,
            u'submissionSchema': {
                u'$ref': request.resource_path(
                    resource, 'schema', query={'role': EDITION_ROLE}),
            },
            u'targetSchema': {
                u'$ref': request.resource_path(
                    resource, 'schema', query={'role': VIEW_ROLE}),
            },
        }


class EntityCollectionLink(EntityLink):
    """Link for an entity as item of a collection."""
    rel = u'collection'

    def description_object(self, resource):
        request = resource.request
        return {
            u'href': request.resource_path(resource.__parent__),
            u'rel': 'collection',
            u'title': self._cw.__('{0}_plural').format(self.entity.cw_etype),
            u'targetSchema': {
                u'$ref': request.resource_path(
                    resource.__parent__, 'schema'),
            },
        }


class EntityRelatedLink(EntityLink):
    """Link to (`rtype`, `role`) relation from `entity` as `role`.
    """
    __regid__ = 'jsonschema.relation'
    __select__ = (match_kwargs('entity', 'rtype', 'role')
                  & score_entity(lambda x: x.has_eid()))

    def description_object(self, resource):
        request = resource.request
        assert resource.__class__.__name__ == 'EntityResource'  # XXX debug
        entity = self.cw_extra_kwargs['entity']
        rtype = self.cw_extra_kwargs['rtype']
        role = self.cw_extra_kwargs['role']
        collection_mapper = self._cw.vreg['mappers'].select(
            'jsonschema.collection', self._cw,
            entity=entity, rtype=rtype, role=role)
        title = collection_mapper.title
        return {
            u'href': request.resource_path(resource[rtype]),
            u'rel': u'related',
            u'title': title,
        }


class RelatedCollectionLink(CollectionLink):
    """rel="self" link for collection of related entities."""
    __select__ = match_kwargs('rtype', 'role')
    rel = 'self'

    @property
    def title(self):
        rtype = self.cw_extra_kwargs['rtype']
        role = self.cw_extra_kwargs['role']
        return self._cw._(rtype + ('-object' if role == 'object' else ''))

    def description_object(self, resource):
        request = resource.request
        ldo = super(RelatedCollectionLink, self).description_object(
            resource)
        ldo['targetSchema']['$ref'] = request.resource_path(
            resource, 'schema', query={'role': VIEW_ROLE})
        return ldo


class WorkflowTransitionsEntityLink(EntityLink):
    """Link pointing to workflow transitions of an entity."""
    __select__ = (
        EntityLink.__select__
        & score_entity(lambda x: x.cw_adapt_to('IWorkflowable') is not None)
    )

    def description_object(self, resource):
        request = resource.request
        return {
            'href': request.resource_path(resource['workflow-transitions']),
            'rel': tag_uri(2017, 'workflow-transitions'),
            'title': request.cw_request._('workflow history'),
        }
