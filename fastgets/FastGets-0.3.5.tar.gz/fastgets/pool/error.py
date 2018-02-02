# coding: utf8

from ..core.client import get_client
from ..utils import to_hash
from ..task import Task


class CrawlErrorPool(object):

    @classmethod
    def add(cls, task):
        assert task.crawl_error_traceback

        client = get_client()

        key = '{}:crawl_error_pool'.format(task.instance_id)
        if client.llen(key) < 50:
            client.lpush(key, task.to_json())
            return

        key = '{}:crawl_error_hash_pool'.format(task.instance_id)
        hash_value = to_hash(task.process_error_traceback)
        if client.hlen(key) > 50:
            # 避免异常情况
            return
        elif client.hexists(key, hash_value):
            # 同类错误已经存在
            return
        else:
            client.hset(key, hash_value, task.to_json())

    @classmethod
    def get_tasks(cls, instance_id):
        key = '{}:crawl_error_pool'.format(instance_id)
        tasks = [
            Task.from_json(task_json)
            for task_json in get_client().lrange(key, 0, -1)
        ]

        key = '{}:crawl_error_hash_pool'.format(instance_id)
        tasks.extend([
            Task.from_json(task_json)
            for task_json in get_client().hgetall(key).values()
        ])

        return tasks  # 应该不会有重复的


class ProcessErrorPool(object):

    @classmethod
    def add(cls, task):
        # assert task.page_raw
        assert task.process_error_traceback

        key = '{}:process_error_pool'.format(task.instance_id)
        if get_client().llen(key) < 50:
            get_client().lpush(key, task.to_json())
            return

        key = '{}:process_error_hash_pool'.format(task.instance_id)
        hash_value = to_hash(task.process_error_traceback)
        if get_client().hlen(key) > 50:
            # 避免异常情况
            return
        elif get_client().hexists(key, hash_value):
            # 同类错误已经存在
            return
        else:
            get_client().hset(key, hash_value, task.to_json())

    @classmethod
    def get_tasks(cls, instance_id):
        key = '{}:process_error_pool'.format(instance_id)
        tasks = [
            Task.from_json(task_json)
            for task_json in get_client().lrange(key, 0, -1)
        ]

        key = '{}:process_error_hash_pool'.format(instance_id)

        tasks.extend([
            Task.from_json(task_json)
            for task_json in get_client().hgetall(key).values()
        ])

        return tasks  # 应该不会有重复的
