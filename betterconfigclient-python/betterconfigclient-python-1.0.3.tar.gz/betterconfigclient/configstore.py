import datetime
import logging
import sys
from requests import HTTPError
from .interfaces import ConfigStore
from .readwritelock import ReadWriteLock

log = logging.getLogger(sys.modules[__name__].__name__)


class InMemoryConfigStore(ConfigStore):

    def __init__(self, config_fetcher, time_to_live_seconds):
        super(InMemoryConfigStore, self).__init__(config_fetcher)
        self._lock = ReadWriteLock()
        self._config = None
        self._last_updated = None
        self._config_fetcher = config_fetcher
        self._time_to_live = datetime.timedelta(seconds=time_to_live_seconds)

    def get(self):
        try:
            self._lock.acquire_read()

            utc_now = datetime.datetime.utcnow()
            if self._config is not None \
                    and self._last_updated is not None \
                    and self._last_updated + self._time_to_live > utc_now:
                return self._config
        finally:
            self._lock.release_read()

        try:
            self._lock.acquire_write()

            utc_now = datetime.datetime.utcnow()
            if self._config is not None \
                    and self._last_updated is not None \
                    and self._last_updated + self._time_to_live > utc_now:
                return self._config

            try:
                json = self._config_fetcher.get_configuration_json()
                self._config = json
                self._last_updated = utc_now
            except HTTPError as e:
                log.error('Received unexpected response from ConfigFetcher ' + str(e.response))
            except:
                log.exception(sys.exc_info()[0])
        finally:
            self._lock.release_write()

        return self._config

    def invalidate_cache(self):
        try:
            self._lock.acquire_write()
            self._last_updated = None
        finally:
            self._lock.release_write()
