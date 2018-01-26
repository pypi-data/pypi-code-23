from django.db import models
from cxc_gis.models import Region


class LocationField(models.Field):

    description = "A location"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 80

    def db_type(self, connection):
        return "char({})".format(self.max_length)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        return Region.from_json_string(value)

    def get_prep_value(self, value):
        return value.json
