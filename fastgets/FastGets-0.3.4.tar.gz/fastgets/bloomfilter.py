# coding: utf8

from .utils import to_hash


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):

    def __init__(self, conn):
        # https://hur.st/bloomfilter?n=4000000&p=1.0E-4
        # 错误率 0.0001
        # 数量 > 4,000,000
        self.conn = conn
        self.cap = 1 << 27  # 16M
        self.seeds = [5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 37, 44, 61]  # k=13

    def get_loc(self, seed, md5_string):
        hash_ret = 0
        for i in range(len(md5_string)):
            hash_ret += seed * hash_ret + ord(md5_string[i])
        return (self.cap - 1) & hash_ret

    @classmethod
    def create_key(cls, instance_id):
        return '{}:bloom_filter'.format(instance_id)

    def exists(self, instance_id, string):
        hash_string = to_hash(string)
        key = self.create_key(instance_id)

        with self.conn.pipeline() as pipe:
            for seed in self.seeds:
                pipe.getbit(key, self.get_loc(seed, hash_string))
            return all(pipe.execute())  # 全部是1

    def add(self, instance_id, string):
        hash_string = to_hash(string)
        key = self.create_key(instance_id)

        with self.conn.pipeline() as pipe:
            for seed in self.seeds:
                pipe.setbit(key, self.get_loc(seed, hash_string), 1)
            pipe.execute()

    def init(self):
        from . import env
        self.conn.setbit(self.create_key(env.instance_id), self.cap-1, 1)
