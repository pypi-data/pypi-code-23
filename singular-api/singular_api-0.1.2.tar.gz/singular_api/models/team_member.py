from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin,
        )

from .user import User

class TeamMember(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin
        ):
    COMPLEX_FIELDS = {
            "user": User
            }
    RO_FIELDS = (
        "id",
            )
    W_FIELDS = (
        "user",
        "is_operator",
        "alias",
        "team",
            )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id, client, dictionary)
