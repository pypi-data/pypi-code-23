from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin
        )

class UserData(
        BaseModel, GetAllMixin, GetSpecificMixin
        ):
    COMPLEX_FIELDS = {}
    RO_FIELDS = (
            "id",
            "username",
            "email",
            )
    W_FIELDS = (
    )
    FIELDS = RO_FIELDS = W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id, client, dictionary)
