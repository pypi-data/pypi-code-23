# coding: utf-8
"""This module is responsible to hold out
query compilers. It's main goal is to hold
all the classes and objects responsible to
compile a specific query the dev chose
and write that as a TileStache query.

This uses the Django machinery to do
all that with some specifics
"""
from django.db import connections
from django.contrib.gis.db.models import (
    PointField,
    MultiPointField,
    LineStringField,
    MultiLineStringField,
    PolygonField,
    MultiPolygonField
)


class TileStacheQueryCompiler(object):

    GEOMETRY_FIELDS = (
        PointField,
        MultiPointField,
        LineStringField,
        MultiLineStringField,
        PolygonField,
        MultiPolygonField
    )

    BLACKLIST_FIELDS = (
        'id',
        'geometry',
        'geometria',
    )


class VecTilesQueryCompiler(TileStacheQueryCompiler):

    """given a certain model
    and a list of attributes,
    generates the query we need
    to feed tilestache with"""

    def select_attributes(self, queryset, attributes):
        model = queryset.model
        attrs = list()
        if isinstance(attributes, basestring):
            if attributes == '__all__':
                for field in model._meta.fields:
                    if field.name not in self.BLACKLIST_FIELDS and type(field) not in self.GEOMETRY_FIELDS:
                        attrs.append(field)
                return attrs
        else:
            for attr in attributes:
                if attr not in self.BLACKLIST_FIELDS:
                    attrs.append(model._meta.get_field(attr))

            return attrs

        raise ValueError('attributes must be a string with __all__ or a iterable')

    def compile_geometry(self, queryset, geometry_field):
        model = queryset.model
        geometry_field = model._meta.get_field(geometry_field)
        name = geometry_field.name
        if geometry_field.srid != 900913:
            fmt = "ST_Transform({0}, 900913) as __geometry__"
        else:
            fmt = "{0} as __geometry__"
        return fmt.format(name)

    def compile_id(self, id_field=None):
        id_field = id_field or 'id'
        return '{0} as __id__'.format(id_field)

    def compile(self, queryset, attributes, id_field='id', geometry_field='geom', database='default'):
        id_query = self.compile_id(id_field)
        geom_query = self.compile_geometry(queryset, geometry_field)
        attrs = [attr.name for attr in self.select_attributes(queryset, attributes)]
        queryset = queryset.values(*attrs)
        query, params = queryset.query.sql_with_params()
        with connections[database].cursor() as cursor:
            if hasattr(cursor, 'mogrify'):
                query = cursor.mogrify(query, params)
            else:
                # this will not work for: oracle and sqlite, because
                # they don't have the mogrify method. so, if your query
                # has filters, it will probably break
                query = queryset.query.__str__()

        return query.replace(
            'SELECT ',
            "SELECT {0}, {1}, ".format(id_query, geom_query)    
        )
