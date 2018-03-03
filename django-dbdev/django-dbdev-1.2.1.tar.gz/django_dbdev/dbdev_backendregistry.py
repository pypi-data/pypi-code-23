from builtins import object
from django_dbdev.backends.mysql import MySqlBackend
from django_dbdev.backends.postgis import PostGisBackend
from django_dbdev.backends.postgres import PostgresBackend
from django_dbdev.backends.sqlite import SqliteBackend


class DbdevBackendRegistry(object):
    def __init__(self):
        self.backends = {}

    def register(self, dbengine, backendclass):
        self.backends[dbengine] = backendclass


backendregistry = DbdevBackendRegistry()


def register(dbengine, backendclass):
    """
    Register a dbdev backend to be used for the given Django database engine.
    """
    backendregistry.register(dbengine, backendclass)


backendregistry.register('django.db.backends.mysql', MySqlBackend)
backendregistry.register('django.db.backends.postgresql_psycopg2', PostgresBackend)
backendregistry.register('django.contrib.gis.db.backends.postgis', PostGisBackend)
backendregistry.register('django.db.backends.sqlite3', SqliteBackend)
