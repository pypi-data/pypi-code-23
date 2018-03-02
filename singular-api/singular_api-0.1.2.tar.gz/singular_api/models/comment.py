from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin,
        )

class Comment(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin,
        ):
    COMPLEX_FIELDS = {}
    RO_FIELDS = (
        "id",
        "author",
        "created",
        "updated",
        "operation"
            )
    W_FIELDS = (
        "activity",
        "text",
            )
    FIELDS = RO_FIELDS + W_FIELDS


    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id,client,dictionary)
