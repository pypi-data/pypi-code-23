import requests
import logging
import sys
from cachecontrol import CacheControl
from betterconfigclient.interfaces import ConfigFetcher
from betterconfigclient.version import BETTERCONFIGCLIENT_VERSION

BASE_URI = 'https://cdn.betterconfig.com/configuration-files/'
BASE_EXTENSION = '/config.json'

log = logging.getLogger(sys.modules[__name__].__name__)


def _headers():
    return {'User-Agent': 'BetterConfigClient-Python/' + BETTERCONFIGCLIENT_VERSION, 'Content-Type': "application/json"}


class CacheControlConfigFetcher(ConfigFetcher):

    def __init__(self, project_secret):
        super().__init__(project_secret)
        self._project_secret = project_secret
        self._session = requests.Session()
        self._request_cache = CacheControl(self._session)

    def get_configuration_json(self):
        log.debug("Fetching configuration from BetterConfig")

        uri = BASE_URI + self._project_secret + BASE_EXTENSION
        response = self._request_cache.get(uri, headers=_headers(), timeout=(10, 30))
        response.raise_for_status()
        json = response.json()

        log.debug("BetterConfig configuration json fetch response code:[%d] Cached:[%s]",
                  response.status_code, response.from_cache)
        return json

    def close(self):
        if self._session:
            self._session.close()
