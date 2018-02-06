# coding: utf-8
from django.utils.translation import ugettext_lazy as _


SAFE_DIRS_CHOICE = u'safe'
PORTABLE_DIRS_CHOICE = u'portable'

DIRS_CHOICES = (
    (SAFE_DIRS_CHOICE, _(u'Safe')),
    (PORTABLE_DIRS_CHOICE, _(u'Portable')),
)

PROVIDER_VECTOR = u'vector'
PROVIDER_MAPNIK = u'mapnik'
PROVIDER_PROXY = u'proxy'
PROVIDER_EXTERNAL = u'external'

PROVIDER_CHOICES = (
    (PROVIDER_VECTOR, u'Vector'),
    (PROVIDER_MAPNIK, u'Mapnik'),
    (PROVIDER_PROXY, u'Proxy'),
    (PROVIDER_EXTERNAL, u'External'),
)

VECTOR_DRIVER_SHP = u'shapefile'
VECTOR_DRIVER_POSTGRES = u'PostgreSQL'
VECTOR_DRIVER_ORACLE = u'Oracle'
VECTOR_DRIVER_MYSQL = u'MySQL'
VECTOR_DRIVER_SPATIALITE = u'Spatialite'
VECTOR_DRIVER_GEOJSON = u'GeoJSON'

VECTOR_DB_DRIVERS = (VECTOR_DRIVER_POSTGRES,
                     VECTOR_DRIVER_MYSQL,
                     VECTOR_DRIVER_ORACLE,)

VECTOR_FILE_DRIVERS = (VECTOR_DRIVER_SHP,
                       VECTOR_DRIVER_SPATIALITE,
                       VECTOR_DRIVER_GEOJSON,)

VECTOR_DRIVER_CHOICES = (
    (VECTOR_DRIVER_SHP, _(u'Shapefile')),
    (VECTOR_DRIVER_POSTGRES, _(u'PostgreSQL')),
    (VECTOR_DRIVER_ORACLE, _(u'Oracle')),
    (VECTOR_DRIVER_MYSQL, _(u'MySQL')),
    (VECTOR_DRIVER_SPATIALITE, _(u'SpatiaLite')),
    (VECTOR_DRIVER_GEOJSON, _(u'GeoJSON')),
)
