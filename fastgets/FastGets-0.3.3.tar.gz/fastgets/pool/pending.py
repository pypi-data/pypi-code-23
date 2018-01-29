# coding: utf8

import datetime
from .. import env
from ..core.client import get_client
from ..core.errors import FrameError
from ..core.log import logger
from ..task import Task
from .running import RunningPool


class PendingPool(object):

    @classmethod
    def create_key(cls, instance_id):
        return '{}:{}'.format('pending_pool', instance_id)

    @classmethod
    def get_current_task_num(cls, instance_id):
        return get_client().llen(cls.create_key(instance_id))

    @classmethod
    def add(cls, task):
        assert task.id
        assert task.second_rate_limit
        assert task.instance_id

        task.save()
        key = cls.create_key(task.instance_id)
        get_client().lpush(key, task.id)

    @classmethod
    def fetch(cls, instance_id):
        if env.mode == env.WORK:
            task_id = get_client().rpoplpush(
                cls.create_key(instance_id),
                RunningPool.create_key(instance_id)
            )
        else:
            task_id = get_client().rpop(cls.create_key(instance_id))

        if task_id:
            if isinstance(task_id, bytes):
                # mock redis 无法保证返回 str
                task_id = task_id.decode('utf8')

            task = Task.get(task_id)
            assert task

            task.start_at = datetime.datetime.now()
            task.save()

            return task
