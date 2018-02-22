
from django.db import models
from django_framework.django_helpers.model_helpers import register_model


from django_framework.django_helpers.model_helpers import BaseModel

from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField


class ProfileMSBaseModel(BaseModel):
    # The Base InsightProfile model that all other types has a one to one relationship with
    # you cannot create this oen via the API, instead you must create it via the a specific type!
    # that type's manager will then create the InsightProfile for you and link it up.


    # this overrides the base UUID field so that it can be used to match up the proper profile_uuid! 
    # this allows for cross server communication!
    # remember to update the serializer too!
    uuid = models.UUIDField(db_index=True)  # we override the BASE UUID
    profile_pid = models.IntegerField(db_index = True)

    class Meta:
        abstract = True