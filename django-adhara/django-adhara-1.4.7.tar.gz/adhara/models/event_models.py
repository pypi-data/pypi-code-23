from .base_models import AdharaModel
from django.db import models
from ..utilities import get_user_model, get_config


events_list = get_config("EVENTS.INCLUDE")


def is_abstract(event_type):
    if events_list:
        try:
            events_list.index(event_type)
            return False
        except ValueError:
            return True
    else:
        return True


class AdharaEvents(AdharaModel):
    user = models.OneToOneField(get_user_model(), null=False)

    class Meta:
        abstract = True
        app_label = "adhara"


class FirebaseEvents(AdharaEvents):
    registration_token = models.CharField(max_length=255)

    class Meta:
        db_table = "firebase_events"
        abstract = is_abstract("FIREBASE")
