from unittest import TestCase
from threading import currentThread
from restclients_core.util.local_cache import (local_cache, set_cache_value,
                                               get_cache_value, LOCAL_CACHE)


class TestCache(TestCase):
    def test_context(self):
        thread = currentThread()
        with local_cache() as lc:
            v1 = test_method1("init")

            self.assertTrue(thread in LOCAL_CACHE)
            v2 = test_method1("nope, old cached value")
            self.assertEquals(v2, "init")

        self.assertFalse(thread in LOCAL_CACHE)

    def test_decorator(self):
        thread = currentThread()

        @local_cache()
        def use_the_cache():
            v1 = test_method1("init decorator")

            self.assertTrue(thread in LOCAL_CACHE)
            v2 = test_method1("nope, old cached value")
            self.assertEquals(v2, "init decorator")

        use_the_cache()
        self.assertFalse(thread in LOCAL_CACHE)

    def test_no_cache(self):
        v1 = test_method1("init none")
        self.assertEquals(v1, "init none")

        v2 = test_method1("second, none")
        self.assertEquals(v2, "second, none")


def test_method1(val):
    key = "test_method1_key"
    value = get_cache_value(key)
    if value:
        return value

    set_cache_value(key, val)
    return val
