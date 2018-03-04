"""
Some code to pick up database configuration from environment variables and
construct maps suitable for assignment to Django DATABASES. This code can handle
Heroku, Amazon Elastic Beanstalk, PostgreSQL service files (.pg_service.conf),
PostgreSQL password files (.pgpass), and regular libpq variables.

To using the default engine (psycopg2):

    DATABASES = {
        'default': pg_conninfo()
    }

or, to use an alternative engine, explicitly state the engine class:

    DATABASES = {
        'default': pg_conninfo('django.contrib.gis.db.backends.postgis')
    }

"""

from os import environ, path
from subprocess import check_output
try:
    # 2.7
    from urlparse import urlparse, parse_qs
    from ConfigParser import ConfigParser
except ImportError:
    # 3.x
    from urllib.parse import urlparse, parse_qs
    from configparser import ConfigParser

import pgpasslib

def pg_conninfo(engine='django.db.backends.postgresql'):
    # Default values
    host = 'localhost'
    port = 5432
    database = user = environ.get('USER')
    password = ''
    options = {}

    if 'DATABASE_URL' in environ:
        # Heroku, etc.
        # https://www.postgresql.org/docs/current/static/libpq-connect.html#AEN45347
        url = urlparse(environ.get('DATABASE_URL'))

        host = url.hostname or host
        port = url.port or port
        database = url.path[1:] or database
        user = url.username or user
        password = url.password or password
        options = dict(options, **parse_qs(url.query))

    elif 'RDS_DB_NAME' in environ:
        # AWS Elastic Beanstalk
        # http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-rds.html

        host = environ.get('RDS_HOSTNAME')
        port = environ.get('RDS_PORT')
        database = environ.get('RDS_DB_NAME')
        user = environ.get('RDS_USERNAME')
        password = environ.get('RDS_PASSWORD')

    elif 'PGSERVICE' in environ:
        # Connection Service File
        # https://www.postgresql.org/docs/current/static/libpq-pgservice.html
        # https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-PARAMKEYWORDS
        pg_service = environ.get('PGSERVICE')

        # Check per-user service file
        if 'PGSERVICEFILE' in environ:
            pg_service_file = environ.get('PGSERVICEFILE')
        else:
            pg_service_file = path.join(environ.get('HOME'), '.pg_service.conf')

        if not path.isfile(pg_service_file):
            # Check system-wide service file instead
            sys_conf_dir = check_output(['pg_config', '--sysconfdir']).rstrip('\n')
            pg_service_file = path.join(sys_conf_dir, 'pg_service.conf')

        config = ConfigParser({
            'host': host, 'port': port, 'dbname': database, 'user': user, 'password': password,
        })
        config.read(pg_service_file)

        host = config.get(pg_service, 'host')
        port = config.get(pg_service, 'port')
        database = config.get(pg_service, 'dbname')
        user = config.get(pg_service, 'user')
        password = config.get(pg_service, 'password')

    else:
        # libpq
        # https://www.postgresql.org/docs/current/static/libpq-envars.html

        host = environ.get('PGHOST', host)
        port = environ.get('PGPORT', port)
        database = environ.get('PGDATABASE', database)
        user = environ.get('PGUSER', user)
        password = environ.get('PGPASSWORD', password)

    if not password:
        # Get the password from the password file
        # https://www.postgresql.org/docs/current/static/libpq-pgpass.html
        try:
            password = pgpasslib.getpass(host, port, database, user)
        except:
            password = None

    return {
        'ENGINE': engine,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port,
        'NAME': database,
        'OPTIONS': options,
    }
