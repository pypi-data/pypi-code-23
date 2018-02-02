import datetime
from mongoengine import *
from ..utils import create_id, get_current_inner_ip, time_readable


class UnknownError(Document):

    id = StringField(primary_key=True)
    create_at = DateTimeField()
    traceback = ListField(StringField())
    inner_ip = StringField()

    meta = {
        'collection': 'fastgets_unknown_error'
    }

    @classmethod
    def add(cls, traceback):
        cls.objects(id=create_id()).update(
            create_at=datetime.datetime.now(),
            traceback=traceback,
            inner_ip=get_current_inner_ip(),
            upsert=True,
        )

    def to_api_json(self):
        return dict(
            id=self.id,
            create_at=time_readable(self.create_at),
            traceback=self.traceback,
            inner_ip=self.inner_ip
        )

