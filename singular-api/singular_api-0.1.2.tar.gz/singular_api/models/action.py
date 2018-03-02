from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin
        )
class Action(BaseModel, GetAllMixin, GetSpecificMixin):
    FIELDS = (
        "id",
        "activity",
        "asked_user",
        "asking_user",
        "changed",
        "deleted",
        "asked_team",
        "kind"
    )
    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id,client,dictionary)
