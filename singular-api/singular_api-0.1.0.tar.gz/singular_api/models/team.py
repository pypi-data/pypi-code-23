from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin,
        )
from .team_member import TeamMember

class Team(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin
        ):
    COMPLEX_FIELDS = {"members" : [TeamMember]}
    RO_FIELDS = (
        "members",
        "id",
            )
    W_FIELDS = (
        "name",
            )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id, client, dictionary)
