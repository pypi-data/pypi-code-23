import time

import pytest
from tinydb import storages

from .context import cachalot


@pytest.fixture
def cache():
    return cachalot.Cache(size=2, storage=storages.MemoryStorage)


class TestCache:

    def test_expiry(self, cache):
        now = time.time()
        assert int(cache.expiry()) == int(now + 86400)

    def test_clear(self, cache):
        cache.db.purge()
        cache.db.insert({'key': 'test', 'time': 9999999999, 'value': 1})
        assert len(cache.db) == 1
        cache.clear()
        assert len(cache.db) == 0

    def test_get(self, cache):
        cache.db.insert({'key': 'test', 'time': 9999999999, 'value': '1'})
        cache.db.insert({'key': 'test2', 'time': 1, 'value': '2'})
        assert cache.get('test') == 1
        assert cache.get('test2') == None

    def test_insert(self, cache):
        cache.db.purge()
        cache.insert('test', 1)
        assert len(cache.db) == 1
        assert int(cache.db.all()[0]['value']) == 1

    def test_insert_overflow(self, cache):
        cache.db.purge()
        cache.insert('test', 1)
        cache.insert('test2', 2)
        cache.insert('test3', 3)
        assert len(cache.db) == 2
        assert int(cache.db.all()[0]['value']) == 2

    def test_remove(self, cache):
        cache.db.purge()
        cache.db.insert({'key': 'test', 'time': 9999999999, 'value': 1})
        cache.db.insert({'key': 'test2', 'time': 9999999999, 'value': 2})
        cache.remove('test')
        assert len(cache.db) == 1
        assert int(cache.db.all()[0]['value']) == 2

    def test_remove_oldest(self, cache):
        cache.db.purge()
        cache.db.insert({'key': 'test', 'time': 9999999999, 'value': 1})
        cache.db.insert({'key': 'test2', 'time': 9999999999, 'value': 2})
        cache._remove_oldest()
        assert len(cache.db) == 1
        assert int(cache.db.all()[0]['value']) == 2

    def test_remove_expired(self, cache):
        cache.db.purge()
        cache.db.insert({'key': 'test', 'time': 1, 'value': '1'})
        cache.db.insert({'key': 'test2', 'time': 1, 'value': '2'})
        cache._remove_expired()
        assert len(cache.db) == 0
