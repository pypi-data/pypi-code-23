from clickhouse_driver import Client
from clickhouse_driver.defines import DEFAULT_PORT


class ClickHouse(object):

    param_names = [
        'PORT', 'DATABASE', 'USER', 'PASSWORD', 'CLIENT_NAME', 'CIPHERS',
        'CONNECT_TIMEOUT', 'CA_CERTS', 'SEND_RECEIVE_TIMEOUT', 'VERIFY',
        'PREFIX_COMPRESS_BLOCK_SIZE', 'COMPRESSION', 'SECURE', 'SSL_VERSION',
        'SYNC_REQUEST_TIMEOUT'
    ]

    def __init__(self, app=None, config_prefix='CLICKHOUSE'):
        self.config_prefix = config_prefix
        self.client = None
        if app is not None:
            self.init_app(app, config_prefix)

    def init_app(self, app, config_prefix='CLICKHOUSE'):
        """Initialize the `app` for use with this :class:`~ClickHouse`. This is
        called automatically if `app` is passed to :meth:`~ClickHouse.__init__`.

        The app is configured according to the configuration variables
        ``PREFIX_HOST``, ``PREFIX_PORT``, ``PREFIX_DATABASE``,
        ``PREFIX_USER``, ``PREFIX_PASSWORD``, ``PREFIX_CLIENT_NAME``,
        ``PREFIX_CONNECT_TIMEOUT``, ``PREFIX_SEND_RECEIVE_TIMEOUT``,
        ``PREFIX_SYNC_REQUEST_TIMEOUT``, ``PREFIX_COMPRESS_BLOCK_SIZE``,
        ``PREFIX_COMPRESSION``, ``PREFIX_SECURE``, ``PREFIX_VERIFY``,
        ``PREFIX_SSL_VERSION``, ``PREFIX_CA_CERTS`` and  ``PREFIX_CIPHERS``,
        where "PREFIX" defaults to "CLICKHOUSE".

        :param flask.Flask app: the application to configure for use with
           this :class:`~ClickHouse`
        :param str config_prefix: determines the set of configuration
           variables used to configure this :class:`~ClickHouse`
        """
        self.config_prefix = config_prefix

        if 'clickhouse' not in app.extensions:
            app.extensions['clickhouse'] = {}

        if config_prefix in app.extensions['clickhouse']:
            raise Exception('duplicate config_prefix "%s"' % config_prefix)

        def key(suffix):
            return '%s_%s' % (config_prefix, suffix)

        app.config.setdefault(key('HOST'), 'localhost')
        app.config.setdefault(key('PORT'), DEFAULT_PORT)
        app.config.setdefault(key('DATABASE'), app.name)

        if not isinstance(app.config[key('PORT')], int):
            raise TypeError('%s_PORT must be an integer' % config_prefix)

        kwargs = {}

        for param in self.param_names:
            value = app.config.get(key(param))
            if value is not None:
                kwargs[param.lower()] = value

        self.client = Client(app.config[key('HOST')], **kwargs)

        app.extensions['clickhouse'][config_prefix] = self

    def __getattr__(self, name):
        return getattr(self.client, name)
