# -*- coding: utf-8 -*-

import unittest

from classutils import class_cache_result, clear_class_cached_results


class ResettableCachedProperties(object):

    def __init__(self):
        self.reset()

    @property
    @class_cache_result
    def property_1(self):
        self.count += 1
        return self.count

    @property
    @class_cache_result
    def property_2(self):
        self.count += 1
        return self.count

    @clear_class_cached_results
    def reset(self):
        self.count = 0


class TestResettableCachedProperties(unittest.TestCase):

    def test(self):
        result_cacher = ResettableCachedProperties()
        assert result_cacher.property_1 == 1
        assert result_cacher.property_1 == 1
        assert result_cacher.property_2 == 2
        assert result_cacher.property_2 == 2

        result_cacher.reset()

        assert result_cacher.property_2 == 1
        assert result_cacher.property_2 == 1
        assert result_cacher.property_1 == 2
        assert result_cacher.property_1 == 2


if __name__ == u'__main__':
    unittest.main()
