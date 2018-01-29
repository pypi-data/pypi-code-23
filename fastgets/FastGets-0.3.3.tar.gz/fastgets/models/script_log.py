# coding: utf8

from mongoengine import *
from fastgets.utils import time_readable


class ScriptLog(Document):

    id = StringField(primary_key=True)
    name = StringField()
    start_at = DateTimeField()
    end_at = DateTimeField()
    traceback = ListField(StringField())

    meta = {
        'collection': 'fastgets_script_log'
    }

    def to_api_json(self):
        return dict(
            id=self.id,
            name=self.name,
            start_at=self.start_at and time_readable(self.start_at) or None,
            end_at=self.end_at and time_readable(self.end_at) or None,
            traceback=self.traceback
        )
