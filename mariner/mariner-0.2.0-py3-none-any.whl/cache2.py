import atexit
import functools
import hashlib
import json
from typing import Any

import maya
import tinydb
import tinydb_smartcache

from mariner import utils


class Cache:
    """
    Offline cache for search results.
    """

    def __init__(self,
                 *,
                 path: str='~/.cache/mariner/cache.json',
                 timeout: int=86400,
                 length: int=10000,
                 storage: tinydb.storages.Storage=tinydb.storages.JSONStorage,
                 ) -> None:
        self.path = utils.check_path(path)
        self.timeout = timeout
        self.length = length
        self.db = tinydb.TinyDB(self.path, storage)
        self.db.table_class = tinydb_smartcache.SmartCacheTable
        atexit.register(self._remove_old)

    def get(self, key: str) -> Any:
        """
        Get torrent from database.

        Args:
            key: Key hash.

        Returns:
            Cached object.
        """
        entry = tinydb.Query()
        self.db.update({'time': self.timeout()}, entry.key == key)
        value = self.db.search(entry.key == key)
        return json.loads(value)

    def insert(self, key: str, entry: Any) -> None:
        """
        Insert entry into cache.

        Args:
            key: Key hash of the entry to store.
            entry: Object to cache.
        """
        value = json.dumps(entry)
        self.db.insert({'key': key, 'time': self.timeout(), 'value': value})

    def remove(self, key: str) -> None:
        """
        Delete key from cache.

        Args:
            key: Hash key to delete from the cache.
        """
        entry = tinydb.Query()
        self.db.remove(entry.key == key)

    def _remove_old(self) -> None:
        """
        Remove old entries.
        """
        entry = tinydb.Query()
        self.db.remove(entry.time < maya.now())

    def timeout(self) -> maya.MayaDT:
        """
        Return timeout value.

        Returns:
            Timeout value from current time.
        """
        return maya.now().add(seconds=self.timeout)

    # TODO Implement cache length
    def __call__(self, function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            result = ''
            cacheable = True
            try:
                key = ''.join(function.__name__, json.dumps(args))
            except TypeError:
                cacheable = False
            else:
                key_hash = hashlib.md5(key.encode('utf8')).hexdigest()
                value = self.get(key_hash)
                result = json.loads(value)
            finally:
                if not result:
                    result = function(*args, **kwargs)
                    if cacheable:
                        self.insert(key_hash, json.dumps(result))
                return result
        return wrapped
