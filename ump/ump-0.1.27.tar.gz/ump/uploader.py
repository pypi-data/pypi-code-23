# coding: utf8

"""
上传者
将数据上传到远端
默认使用redis队列
"""

import redis


class Uploader(object):

    rds = None

    def __init__(self, redis_url):
        self.rds = redis.StrictRedis.from_url(redis_url)

    def upload(self, redis_key, data):
        """
        上传
        :param redis_key: redis_key不放在init中，是为了可以多个queue公用一个redis连接，防止连接数过多
                        当然代价就是多个queue可能互相影响，但是使用者可以自己选择生成多个uploader实例
        :param data:
        :return:
        """
        return self.rds.rpush(redis_key, data)
