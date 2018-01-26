from restclients_core.models import CacheHTTP
from unittest import TestCase


class TestCacheHTTP(TestCase):

    def test_cache_http(self):
        obj = CacheHTTP()

        obj.cache_class = self.__class__
        self.assertEquals(obj.get_cache_class(), self.__class__)


class SubClassTest(TestCacheHTTP):

    def test_cache_http(self):
        obj = CacheHTTP()

        obj.cache_class = self.__class__
        self.assertEquals(obj.get_cache_class(), SubClassTest)
