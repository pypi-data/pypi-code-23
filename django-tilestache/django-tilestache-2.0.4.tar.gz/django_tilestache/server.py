# coding: utf-8
import requests
import logging
from TileStache import WSGITileServer, parseConfig
from apscheduler.schedulers.background import BackgroundScheduler
logger = logging.getLogger(__name__)


class RemoteConfigurationLoader(object):

    """
    This is a custom Tilestache config
    object.
    This will make requests to the appropriate
    endpoints
    and reconfigure the applicationt
    """

    cache = {}
    layers = {}
    dirpath = None

    def __init__(self, endpoint, auth=None, crash_tilestache=False):
        """
        based on a control
        """
        if not endpoint:
            raise ValueError('endpoint cannot be null')
        self.index = 'text/plain', 'Tilestache rules'
        self.endpoint = endpoint
        self.auth = auth
        self.crash_tilestache = crash_tilestache

    def load_remote_config(self):
        try:
            logger.info('loading remote config at address %s', self.endpoint)
            response = self._fetch_remote_config(
                self.endpoint,
                self.auth
            )
            return self._load_remote_config(response)
        except Exception as ex:
            logger.error('error while loading remote config %s', ex.message)
            if self.crash_tilestache:
                raise

    def _setup_auth(self, auth):

        session = requests.Session()
        if auth and 'token' in auth:
            token = auth.get('token')
            session.headers.update({'Authorization': 'Token {0}'.format(token)})

        if auth and 'user' in auth and 'password' in auth:
            user = auth.get('user')
            password = auth.get('password')
            session.auth = (user, password)

        return session

    def _fetch_remote_config(self, endpoint, auth):
        if not endpoint:
            raise ValueError('you must provide the control endpoint')
        session = self._setup_auth(auth)

        return session.get(endpoint)

    def _load_remote_config(self, response):
        data = response.json()
        return parseConfig(data)


class RemoteTileStache(WSGITileServer, object):

    def configure(self):
        self.config = self.configurator.load_remote_config()

    def __init__(self, endpoint, auth=None, config_timeout=120, crash_tilestache=False):

        """
        initializes a new tilestache server
        which reloads it's configuration every
        timeout
        """

        self.configurator = RemoteConfigurationLoader(
            endpoint=endpoint,
            auth=auth,
            crash_tilestache=crash_tilestache
        )
        self.configure()
        self.config_timeout = config_timeout
        self.scheduler = BackgroundScheduler()
        self.job = self.scheduler.add_job(self.configure, 'interval', seconds=self.config_timeout)
        self.scheduler.start()
        super(RemoteTileStache, self).__init__(config=self.config, autoreload=False)
