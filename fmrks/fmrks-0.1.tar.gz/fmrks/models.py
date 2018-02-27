from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Fmrk(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_create_by",
        on_delete=models.SET_NULL,
    )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    descr = models.CharField(max_length=100, null=True, blank=True)
    lat = models.CharField(max_length=100, )
    lng = models.CharField(max_length=100, )

    def as_dict(self):
        return {
            'date': str(self.create_at),
            "name": self.name,
            'descr': self.descr,
            'lat': self.lat,
            'lng': self.lng,
        }
