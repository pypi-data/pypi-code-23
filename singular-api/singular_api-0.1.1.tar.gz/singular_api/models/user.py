from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, UpdateMixin,
        )
from .user_data import UserData

class User(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, UpdateMixin,
        ):
    COMPLEX_FIELDS = {
            "user": UserData,
            }
    RO_FIELDS = (
            "id",
            "user",
            )
    W_FIELDS = (
        "secondary_emails_list",
        "deleted",
    )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id, client, dictionary)

    def status_change():
        raise NotImplementedError('status_change not yet implemented for'
            '{}'.format(self.__class__))
