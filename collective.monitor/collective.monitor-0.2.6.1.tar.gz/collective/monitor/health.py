from Zope2 import app as App


def ok(connection):
    """fast health check for load balancers that simply returns 'OK'
    """
    connection.write('OK\n')

def db_connected(connection, dbname='main'):
    """returns the string 'OK' if database (default=main) is connected.
    can be used for health checks in load-balancers
    """
    app = App()
    try:
        if app.Control_Panel.Database[dbname]._getDB()._storage.is_connected():
            connection.write('OK\n')
            return
        connection.write('database {} is not connected\n'.format(dbname))
    except KeyError, e:
        connection.write(str(e))
    finally:
        app._p_jar.close()
