# coding: utf8
import threading
import datetime
from mongoengine import *

from ..utils import datetime2utc, time_readable
from ..core.decorators import sync


_cached_instance_ids = []
_cached_at = None


class Instance(Document):

    id = StringField(primary_key=True)
    process_id = StringField()
    name = StringField()
    description = StringField()
    start_at = DateTimeField()
    finish_at = DateTimeField()
    stop_at = DateTimeField()
    update_at = DateTimeField()

    total_task_num = IntField(default=0)
    pending_task_num = IntField(default=0)
    running_task_num = IntField(default=0)
    success_task_num = IntField(default=0)
    crawl_error_task_num = IntField(default=0)
    process_error_task_num = IntField(default=0)

    avg_crawl_seconds = FloatField()
    avg_process_seconds = FloatField()
    task_active_at = DateTimeField()

    traceback = ListField(StringField())

    meta = {
        'collection': 'fastgets_instance',
    }

    @property
    def status(self):
        if self.stop_at:
            return '手动停止'
        elif self.finish_at:
            return '正常完成'
        elif (datetime.datetime.now()-self.update_at).seconds > 3:
            return '异常停止'
        else:
            return '正在运行'

    def is_stopped(self):
        return bool(self.stop_at)

    @classmethod
    def get(cls, id):
        return cls.objects.with_id(id)

    def stop(self):
        Instance.objects(id=self.id).update(set__stop_at=datetime.datetime.now())

    def finish(self):
        Instance.objects(id=self.id).update(set__finish_at=datetime.datetime.now())

    def is_active(self):
        return (datetime.datetime.now() - self.task_active_at).seconds < 30

    def to_api_json(self, **kwargs):
        json_dict = dict(
            id=self.id,
            process_id=self.process_id,
            name=self.name,
            description=self.description,
            start_at=self.start_at and time_readable(self.start_at) or None,
            finish_at=self.finish_at and time_readable(self.finish_at) or None,

            total_task_num=self.total_task_num,
            pending_task_num=self.pending_task_num,
            running_task_num=self.running_task_num,
            success_task_num=self.success_task_num,
            error_task_num=self.crawl_error_task_num+ self.process_error_task_num,
            crawl_error_task_num=self.crawl_error_task_num,
            process_error_task_num=self.process_error_task_num,

            avg_crawl_seconds=self.avg_crawl_seconds,
            avg_process_seconds=self.avg_process_seconds,
            task_active_at=self.task_active_at and time_readable(self.task_active_at) or None,

            status=self.status,
        )
        json_dict.update(kwargs)
        return json_dict

    @classmethod
    @sync(threading.Lock())
    def get_running_ids(cls):
        global _cached_instance_ids, _cached_at
        now = datetime.datetime.now()
        if _cached_instance_ids and (now-_cached_at).seconds < 5:
            return _cached_instance_ids
        else:
            _cached_instance_ids = []
            _cached_at = now
            for each in cls.objects(
                    stop_at__exists=False, update_at__gte=now-datetime.timedelta(seconds=30)
            ).only('id').as_pymongo().no_cache():
                _cached_instance_ids.append(each['_id'])
            return _cached_instance_ids

