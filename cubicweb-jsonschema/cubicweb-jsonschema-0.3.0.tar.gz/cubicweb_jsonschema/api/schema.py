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

"""cubicweb-jsonschema Pyramid views for JSON Schema endpoints."""

from functools import wraps

import json

from pyramid import httpexceptions
from pyramid.renderers import JSON
from pyramid.view import view_config

from cubicweb.web.views import uicfg

from .. import (
    CREATION_ROLE,
    EDITION_ROLE,
    JSONSCHEMA_MEDIA_TYPE,
    VIEW_ROLE,
    resources,
)
from . import (
    describes,
)


def schema_role(*allowed):
    """View decorator that parses the "role" query string parameter and checks
    that it's in `allowed` values.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(context, request):
            role = request.params.get('role')
            if role is not None and role not in allowed:
                raise httpexceptions.HTTPBadRequest(
                    'invalid role: {0}'.format(role))
            return func(context, request)
        return wrapper
    return decorator


def jsonschema_config(**settings):
    for name, value in [
        ('name', 'schema'),
        ('route_name', 'cubicweb-jsonschema.schema'),
        ('accept', JSONSCHEMA_MEDIA_TYPE),
        ('renderer', 'jsonschema'),
        ('request_method', 'GET'),
        ('permission', 'authenticated'),
    ]:
        settings.setdefault(name, value)
    return view_config(**settings)


def links_sortkey(link):
    """key function for sorting a list of link description object."""
    return link['href'], link['rel']


@jsonschema_config(
    context=resources.RootResource,
    decorator=[describes],
)
def application_schema(context, request):
    """Schema view for the application."""
    vreg = request.registry['cubicweb.registry']

    def links():
        for eschema in vreg.schema.entities():
            if uicfg.indexview_etype_section.get(eschema) != 'application':
                continue
            etype = eschema.type
            etype_resource = context[etype]
            title = etype + '_plural'
            link = vreg['links'].select(
                'jsonschema.collection', request.cw_request, title=title)
            yield link.description_object(etype_resource)

    schema = {
        'type': "null",
        'links': sorted(links(), key=links_sortkey),
    }
    cnx = request.cw_cnx
    if cnx is not None:
        schema['title'] = cnx.property_value('ui.site-title')
    return schema


@jsonschema_config(
    context=resources.ETypeResource,
    decorator=[
        describes,
        schema_role(VIEW_ROLE, CREATION_ROLE),
    ],
)
def etype_schema(context, request):
    """Schema view for an entity type.

    In presence of a "role" query parameter, the JSON Schema for specified
    role is returned. Otherwise, the complete JSON Hyper Schema is returned.
    """
    role = request.params.get('role')
    mapper = context.mapper(role)
    return mapper.json_schema(role)


@jsonschema_config(
    context=resources.EntityResource,
    decorator=[
        describes,
        schema_role(VIEW_ROLE, EDITION_ROLE),
    ],
)
def entity_schema(context, request):
    """Schema view for a live entity.

    In presence of a "role" query parameter, the JSON Schema for specified
    role is returned. Otherwise, the complete JSON Hyper Schema is returned.
    """
    role = request.params.get('role')
    mapper = context.mapper(role)
    return mapper.json_schema(role)


@jsonschema_config(
    context=resources.RelatedEntitiesResource,
    decorator=[
        describes,
        schema_role(VIEW_ROLE, CREATION_ROLE),
    ],
)
def related_entities_schema(context, request):
    """Schema view for the collection of targets of a relation.
    """
    role = request.params.get('role')
    mapper = context.mapper(role)
    return mapper.json_schema(role)


@jsonschema_config(
    context=resources.RelatedEntityResource,
    decorator=[
        describes,
        schema_role(VIEW_ROLE, EDITION_ROLE),
    ],
)
def related_entity_schema(context, request):
    """Schema view for a target entity of a relation.

    In presence of a "role" query parameter, the JSON Schema for specified
    role is returned. Otherwise, the complete JSON Hyper Schema is returned.
    """
    role = request.params.get('role')
    mapper = context.mapper(role)
    return mapper.json_schema(role)


@jsonschema_config(
    context=resources.WorkflowTransitionsResource,
    decorator=[
        describes,
        schema_role(VIEW_ROLE, CREATION_ROLE),
    ],
)
def entity_workflow_transitions(context, request):
    """Schema view for workflow transitions of an entity."""
    role = request.params.get('role')
    mapper = context.mapper(role)
    return mapper.json_schema(role)


def includeme(config):
    config.include('..predicates')
    config.add_route(
        'cubicweb-jsonschema.schema',
        '*traverse',
        factory=resources.RootResource,
        strict_accept=JSONSCHEMA_MEDIA_TYPE,
    )

    def jsonschema_dumps(value, **kwargs):
        value.setdefault(
            '$schema',
            'http://json-schema.org/draft-06/schema#',
        )
        return json.dumps(value, **kwargs)

    config.add_renderer(
        'jsonschema',
        JSON(serializer=jsonschema_dumps),
    )
    config.scan(__name__)
