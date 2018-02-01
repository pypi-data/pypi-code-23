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

"""cubicweb-jsonschema Pyramid "entities" resources definitions."""

import abc
from collections import defaultdict
from functools import wraps

from six import text_type, add_metaclass

from pyramid.decorator import reify
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPNotFound,
)
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    DENY_ALL,
)

from ._compat import ABCMeta
from .api import json_problem

from rql import nodes, TypeResolverException


def parent(init_method):
    """Decorator for resource class's __init__ method to bind the __parent__
    attribute to instance.
    """
    @wraps(init_method)
    def wrapper(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        init_method(self, *args, **kwargs)
        self.__parent__ = parent

    return wrapper


def find_relationship(schema, etype, rtype, role='subject'):
    """Return (`rtype`, `role`) if `etype` has a relationship `rtype` else
    raise a ValueError.
    """
    eschema = schema[etype]
    for relinfo in eschema.relation_definitions():
        rschema, __, role = relinfo
        if rschema.final or rschema.meta:
            continue
        if rschema.type == rtype and role == role:
            return relinfo
    raise ValueError('-'.join([rtype, role]))


def need_cnx(func):
    """Method decorator checking if the request is bound to an authenticated
    user (for which request.cw_cnx is not None).
    """
    @wraps(func)
    def wrapped_method(self):
        cnx = self.request.cw_cnx
        if cnx is None:
            raise HTTPForbidden()
        return func(self, cnx)
    return wrapped_method


class _PluggableResourceType(type):
    """Metaclass for pluggable resources, ensuring they have their own
    _child_resources dictionary.
    """
    def __init__(cls, *args, **kwargs):
        super(_PluggableResourceType, cls).__init__(*args, **kwargs)
        cls._child_resources = defaultdict(list)


@add_metaclass(_PluggableResourceType)
class PluggableResource(object):
    """Base class for pluggable resources, which provides an API to register
    custom child resources.

    .. automethod: child_resource
    """

    @classmethod
    def child_resource(cls, child_resource):
        """Register `child_resource`, that should be a class inheriting from
        :class:`TraversalResource`.

        It may be used as a class decorator.
        """
        cls._child_resources[child_resource.segment].append(child_resource)
        return child_resource

    def matching_resource(self, value):
        """Return the resource matching `value` child segment or None if no one
        matches.

        If there are more than on matching resource, raises `ValueError`.
        """
        matches = []
        for child_resource in self._child_resources[value]:
            if child_resource.match(self):
                matches.append(child_resource(self.request, self))

        if matches:
            if len(matches) > 1:
                msg = 'more than one matching resources: {}'.format(matches)
                raise ValueError(msg)
            return matches[0]
        return None

    def __getitem__(self, value):
        # Make sure parent class has no __getitem__ as we do not call it here.
        # If it happens, we'll need to call it here.
        assert not hasattr(super(PluggableResource, self), '__getitem__')
        child_resource = self.matching_resource(value)
        if child_resource is None:
            raise KeyError(value)
        return child_resource


@add_metaclass(abc.ABCMeta)
class TraversalResource(object):
    """Abstract base class for custom child resource. Concrete classes should
    specify both `segment` class attribute and `match` method.
    """
    #: string indicating the matched segment,
    segment = None

    @abc.abstractmethod
    def match(parent_resource):
        """Take the parent resource's instance as argument and returning `True`
        if this resource applies to this context or `False` otherwise.
        """

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent
        self.__name__ = self.segment


@add_metaclass(ABCMeta)
class Mappable(object):
    """Abstract class for resources associated with a mapper."""

    @abc.abstractmethod
    def mapper(self, schema_role=None):
        """Return the mapper associated with this resource."""


class RootResource(PluggableResource):
    """Root resources for entities."""
    __parent__ = None
    __name__ = ''
    __acl__ = [
        # We need Authenticated because we rely on request.cw_cnx to be set
        # (it's None for unauthenticated users). No distinction is made
        # between CubicWeb's anonymous user and other kind of users.
        (Allow, Authenticated, ALL_PERMISSIONS),
        DENY_ALL,
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, value):
        try:
            return super(RootResource, self).__getitem__(value)
        except KeyError:
            pass
        try:
            return ETypeResource(self.request, value, self)
        except KeyError:
            raise KeyError(value)


class Paginable(object):
    """ A paginable resource"""
    def __init__(self, request):
        self.request = request
        cnx = request.cw_cnx
        if cnx is not None:
            default_limit = cnx.property_value('navigation.page-size')
        else:
            default_limit = 40
        req_limit = request.params.get('limit', default_limit)
        req_offset = request.params.get('offset', 0)
        try:
            self.limit = int(req_limit)
            self.offset = int(req_offset)
        except ValueError:
            detail = 'invalid limit ({}) or offset ({})'.format(
                req_limit, req_offset)
            raise json_problem(status=400, detail=detail)
        if self.limit < 1:
            detail = 'invalid limit: {}'.format(self.limit)
            raise json_problem(status=400, detail=detail)
        self._has_next = False

    def prev_link(self):
        if self.offset > 0:
            previous_offset = max(self.offset - self.limit, 0)
            query = {
                "limit": self.limit,
                "offset": previous_offset,
            }
            href = self.request.resource_path(self, query=sorted(query.items()))
            return {"href": href, "type": "application/json"}
        return None

    def next_link(self):
        if self._has_next:
            next_offset = self.offset + self.limit
            query = {
                "limit": self.limit,
                "offset": next_offset,
            }
            href = self.request.resource_path(self, query=sorted(query.items()))
            return {"href": href, "type": "application/json"}
        return None

    def paginate(self, select, args=None):
        select.set_limit(self.limit+1)
        select.set_offset(self.offset)
        rql = select.as_string()
        rset = self.request.cw_cnx.execute(rql, args)
        if len(rset) == self.limit + 1:
            self._has_next = True
            rset = rset.limit(self.limit)
        return rset


@Mappable.register
class ETypeResource(Paginable, PluggableResource):
    """A resource class for an entity type."""

    @classmethod
    def from_match(cls, matchname):
        def factory(request):
            return cls(request, request.matchdict[matchname])
        return factory

    def __init__(self, request, etype, parent=None):
        super(ETypeResource, self).__init__(request)
        vreg = request.registry['cubicweb.registry']
        self.request = request
        self.etype = vreg.case_insensitive_etypes[etype.lower()]
        self.cls = vreg['etypes'].etype_class(self.etype)
        if parent is None:
            parent = RootResource(request)
        self.__parent__ = parent
        self.__name__ = self.etype.lower()

    @property
    def title(self):
        return self.request.cw_request.__('{}_plural'.format(self.etype))

    def __getitem__(self, value):
        try:
            return super(ETypeResource, self).__getitem__(value)
        except KeyError:
            pass
        for attrname in ('eid', self.cls.cw_rest_attr_info()[0]):
            resource = EntityResource(self.request, self.cls,
                                      attrname, value, self)
            try:
                rset = resource.rset
            except HTTPNotFound:
                continue
            if rset.rowcount:
                return resource
        raise KeyError(value)

    @reify
    @need_cnx
    def rset(self, cnx):
        select = self.cls.fetch_rqlst(cnx.user)
        return self.paginate(select)

    def mapper(self, schema_role=None):
        vreg = self.request.registry['cubicweb.registry']
        return vreg['mappers'].select(
            'jsonschema.collection', self.request.cw_request,
            etype=self.etype, resource=self)


@Mappable.register
class EntityResource(PluggableResource):
    """A resource class for an entity. It provide method to retrieve an entity
    by eid.
    """

    def __init__(self, request, cls, attrname, name, parent):
        self.request = request
        self.cls = cls
        self.attrname = attrname
        self.__name__ = name
        self.__parent__ = parent

    @property
    def title(self):
        return self.rset.one().dc_title()

    def __getitem__(self, value):
        vreg = self.request.registry['cubicweb.registry']
        schema = vreg.schema
        try:
            return super(EntityResource, self).__getitem__(value)
        except KeyError:
            pass
        prefix = 'reverse-'
        if value.startswith(prefix):
            rtype, role = value[len(prefix):], 'object'
        else:
            rtype, role = value, 'subject'
        try:
            rschema, __, role = find_relationship(
                schema, self.cls.cw_etype, rtype, role=role)
        except ValueError:
            raise KeyError(value)
        else:
            return RelatedEntitiesResource(
                self.request, rschema.type, role, parent=self)

    @reify
    @need_cnx
    def rset(self, cnx):
        if self.cls is None:
            return cnx.execute('Any X WHERE X eid %(x)s',
                               {'x': int(self.__name__)})
        st = self.cls.fetch_rqlst(cnx.user, ordermethod=None)
        st.add_constant_restriction(st.get_variable('X'), self.attrname,
                                    'x', 'Substitute')
        if self.attrname == 'eid':
            try:
                rset = cnx.execute(st.as_string(), {'x': int(self.__name__)})
            except (ValueError, TypeResolverException):
                # conflicting eid/type
                raise HTTPNotFound()
        else:
            rset = cnx.execute(st.as_string(), {'x': text_type(self.__name__)})
        return rset

    def mapper(self, schema_role=None):
        vreg = self.request.registry['cubicweb.registry']
        entity = self.rset.one()
        return vreg['mappers'].select(
            'jsonschema.entity', self.request.cw_request,
            entity=entity, resource=self)


@Mappable.register
@EntityResource.child_resource
class WorkflowTransitionsResource(TraversalResource):
    """Resource for workflow transitions of an entity."""
    segment = 'workflow-transitions'

    @classmethod
    def match(cls, parent_resource):
        entity = parent_resource.rset.one()
        return entity.cw_adapt_to('IWorkflowable') is not None

    @property
    def for_entity(self):
        return self.__parent__.rset.one()

    def mapper(self, schema_role=None):
        vreg = self.request.registry['cubicweb.registry']
        return vreg['mappers'].select(
            'jsonschema.collection', self.request.cw_request,
            etype='TrInfo', for_entity=self.for_entity, resource=self)


@Mappable.register
class RelatedEntitiesResource(Paginable, PluggableResource):
    """A resource wrapping entities related to the entity bound to
    `entity_resource` through `rtype`/`role`.
    """

    @parent
    def __init__(self, request, rtype, role, **kwargs):
        super(RelatedEntitiesResource, self).__init__(request)
        self.request = request
        self.rtype = rtype
        self.role = role
        if role == 'object':
            self.__name__ = 'reverse-' + rtype
        else:
            self.__name__ = rtype

    @property
    def title(self):
        return self.request.cw_request.__(
            self.rtype + ('_object' if self.role == 'object' else ''))

    @reify
    @need_cnx
    def rset(self, cnx):
        # May raise HTTPNotFound, this is probably fine (isn't it?)
        entity = self.__parent__.rset.one()
        vreg = self.request.registry['cubicweb.registry']
        # XXX Until https://www.cubicweb.org/ticket/12306543 gets done.
        rql = entity.cw_related_rql(self.rtype, role=self.role)
        args = {'x': entity.eid}
        select = vreg.parse(entity._cw, rql, args).children[0]
        mainvar = select.get_variable('X')
        sortterms = self.request.params.get('sort')
        if sortterms:
            self._handle_sort_terms(select, mainvar, sortterms)
        return self.paginate(select, args)

    @staticmethod
    def _handle_sort_terms(select, mainvar, sortterms):
        select.remove_sort_terms()
        for term in sortterms.split(','):
            if term.startswith('-'):
                asc = False
                term = term[1:]
            else:
                asc = True
            mdvar = select.make_variable()
            rel = nodes.make_relation(mainvar, term,
                                      (mdvar,), nodes.VariableRef)
            select.add_restriction(rel)
            select.add_sort_var(mdvar, asc=asc)

    def __getitem__(self, value):
        try:
            return super(RelatedEntitiesResource, self).__getitem__(value)
        except KeyError:
            pass
        entity = self.__parent__.rset.one()
        if self.role == 'object':
            mvar = 'S'
            args = {'s': value, 'o': entity.eid}
        else:
            mvar = 'O'
            args = {'s': entity.eid, 'o': value}
        rset = self.request.cw_cnx.execute(
            'Any {mvar} WHERE O eid %(o)s, S {rtype} O, S eid %(s)s'.format(
                mvar=mvar, rtype=self.rtype),
            args)
        if not rset:
            raise KeyError(value)
        return RelatedEntityResource(
            self.request, rset.one(), rtype=self.rtype, role=self.role,
            parent=self)

    def mapper(self, schema_role=None):
        vreg = self.request.registry['cubicweb.registry']
        entity = self.__parent__.rset.one()
        return vreg['mappers'].select(
            'jsonschema.collection', self.request.cw_request,
            entity=entity, rtype=self.rtype, role=self.role,
            resource=self)


@Mappable.register
class RelatedEntityResource(PluggableResource):
    """A resource an entity related to another one."""

    def __init__(self, request, entity, rtype, role, parent):
        self.request = request
        self.entity = entity
        self.rtype = rtype
        self.role = role
        self.__parent__ = parent
        self.__name__ = text_type(entity.eid)

    @property
    def title(self):
        return self.entity.dc_title()

    def mapper(self, schema_role=None):
        vreg = self.request.registry['cubicweb.registry']
        parent = self.__parent__
        return vreg['mappers'].select(
            'jsonschema.entity', self.request.cw_request,
            entity=self.entity, rtype=parent.rtype, role=parent.role,
            resource=self)
