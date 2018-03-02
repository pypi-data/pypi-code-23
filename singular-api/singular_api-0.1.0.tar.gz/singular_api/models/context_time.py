from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin,
        )

class ContextTime(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin
        ):
    COMPLEX_FIELDS = {}
    RO_FIELDS = (
        "id",
        )
    W_FIELDS = (
        "context",
        "active_from",
        "active_until",
        "duration",
        "excluding",
        "start"
        )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id,client,dictionary)
