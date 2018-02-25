from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

UserModel = get_user_model()

on_delete = getattr(settings, 'DJEXT_BLAME_ON_DELETE', models.SET_NULL)
if hasattr(settings, 'DJEXT_BLAME_NULLABLE'):
    null = bool(getattr(settings, 'DJEXT_BLAME_NULLABLE'))
else:
    null = on_delete == models.SET_NULL


class BaseBlameModel(models.Model):
    created_by = models.ForeignKey(UserModel, related_name='+', on_delete=on_delete, null=null)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(UserModel, related_name='+', on_delete=on_delete, null=null)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
