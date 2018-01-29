# coding: utf8

import redis
import mockredis
from .. import env


_client = None


def get_client():
    global _client
    if not _client:
        if env.mode in [env.DISTRIBUTED, env.WORK, env.API]:
            _config = dict(env.REDIS_CONFIG)
            _config['decode_responses'] = True
            _client = redis.Redis(**_config)
        else:
            # local or unittest
            _client = mockredis.MockRedis(decode_responses=True)

    return _client


_filter_client = None


def get_filter_client():
    from ..bloomfilter import BloomFilter
    global _filter_client
    if not _filter_client:
        _filter_client = BloomFilter(get_client())
    return _filter_client
