import psycopg2
import urllib
import traceback
import sys
from contextlib import contextmanager


def get_libpq_connection_string_from_url(database_url):
    """
    Returns a libpq connection string parsed from the passed database_url

    Encoded passwords should be unencoded since psycopg2 doesn't support encoded ones:
    >>> get_libpq_connection_string_from_url('postgres://dbuser:rfASFNBq2%269vn23io4asAhas%3fNEd@database.hooli.com/hoolibase')
    'host=database.hooli.com dbname=hoolibase user=dbuser password=rfASFNBq2&9vn23io4asAhas?NEd'

    Same goes for encoded usernames:
    >>> get_libpq_connection_string_from_url('postgres://db%2duser:rfASFNBq29vn23io4asAhasNEd@database.hooli.com/hoolibase')
    'host=database.hooli.com dbname=hoolibase user=db-user password=rfASFNBq29vn23io4asAhasNEd'

    and encoded database names:
    >>> get_libpq_connection_string_from_url('postgres://dbuser:rfASFNBq29vn23io4asAhasNEd@database.hooli.com/hooli%23base')
    'host=database.hooli.com dbname=hooli#base user=dbuser password=rfASFNBq29vn23io4asAhasNEd'

    Supports no password:
    >>> get_libpq_connection_string_from_url('postgres://dbuser@database.hooli.com/hoolibase')
    'host=database.hooli.com dbname=hoolibase user=dbuser'

    Supports no username and no password:
    >>> get_libpq_connection_string_from_url('postgres://database.hooli.com/hoolibase')
    'host=database.hooli.com dbname=hoolibase'
    """
    database_url = urllib.unquote(database_url)
    database_url_sans_protocol = database_url.split('://')[1]
    database_name = database_url_sans_protocol.split('/')[-1]

    has_user = '@' in database_url_sans_protocol
    database_host = database_url_sans_protocol.split('@')[1].split('/')[0] if has_user else database_url_sans_protocol.split('/')[0]

    has_password = ':' in database_url_sans_protocol.split('@')[0]
    database_user = database_url_sans_protocol.split(':')[0] if has_password else database_url_sans_protocol.split('@')[0]
    database_password = database_url_sans_protocol.split(':')[1].split('@')[0] if has_password else None

    libq_connection_string = 'host={host} dbname={name}'.format(host=database_host, name=database_name)
    if has_user:
        libq_connection_string += ' user={}'.format(database_user)
    if has_password:
        libq_connection_string += ' password={}'.format(database_password)
    return libq_connection_string

@contextmanager
def database_connection(database_url):
    DATABASE_CONNECTION_STRING = get_libpq_connection_string_from_url(database_url)
    try:
        with psycopg2.connect(DATABASE_CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                yield cursor
        conn.close()
    except Exception as exception:
        print(traceback.format_exc())
        print('Unable to run query')
        raise exception

if __name__ == '__main__':
    import doctest
    failing_tests = doctest.testmod()[0]
    sys.exit(1 if failing_tests else 0)
