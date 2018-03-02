from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin,
        )
from .user import User
from .context_time import ContextTime

class Context(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin
        ):
    COMPLEX_FIELDS = {}
    RO_FIELDS = (
            "id",
            "owner",
            "parent",
            )
    W_FIELDS = (
            'time',
            'name',
            'daily_limit',
            'weekly_limit',
            'monthly_limit',
            'default',
            )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id,client,dictionary)

Context.COMPLEX_FIELDS = {
        "owner" : User,
        "time" : [ContextTime],
        }
