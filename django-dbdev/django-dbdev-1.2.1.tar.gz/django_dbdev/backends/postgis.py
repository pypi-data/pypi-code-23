from .postgres import PostgresBackend

DBSETTINGS = {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'PORT': 20021,
    'NAME': 'dbdev',
    'USER': 'dbdev',
    'PASSWORD': 'dbdev',
    'HOST': '127.0.0.1',
}


class PostGisBackend(PostgresBackend):
    """
    This is pretty much just an alias.. Nothing should need to be different.. Just the DBSETTINGS above :)
    """