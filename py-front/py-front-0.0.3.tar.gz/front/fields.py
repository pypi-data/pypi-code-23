from datetime import datetime

from marshmallow import fields

from front import util


class UnixEpochDateTime(fields.DateTime):
    DATEFORMAT_SERIALIZATION_FUNCS = {
        'epoch': util.datetime_to_utc_timestamp,
    }

    DATEFORMAT_DESERIALIZATION_FUNCS = {
        'epoch': datetime.utcfromtimestamp,
    }

    def __init__(self, **kwargs):
        super(UnixEpochDateTime, self).__init__('epoch', **kwargs)
