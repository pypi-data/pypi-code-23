from __future__ import with_statement

import redis

from django.conf import settings


class RedisPoolManager(object):
    pool_manager = redis.BlockingConnectionPool

    def __init__(self, settings):
        self.settings = settings
        self.pools = {}

    def get_pool(self, db_alias):
        if db_alias not in self.pools:
            if not hasattr(self.settings, 'REDISDB') and db_alias == 'default':
                self.pools[db_alias] = self.pool_manager(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DATABASE,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True)
            else:
                params = {}
                config = self.settings.REDISDB[db_alias]
                params['host'] = config.get('HOST', '127.0.0.1')
                params['port'] = config.get('PORT', 6379)
                params['db'] = config.get('DB', 0)
                params['password'] = config.get('PASSWORD', None)
                params['decode_responses'] = True
                self.pools[db_alias] = self.pool_manager(**params)

        return self.pools[db_alias]

redis_pool_manager = RedisPoolManager(settings)
