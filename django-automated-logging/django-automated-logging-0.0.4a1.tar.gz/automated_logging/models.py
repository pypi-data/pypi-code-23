# from .signals import request, database, m2m
from django.conf import settings
import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, pk=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ModelObject(BaseModel):
    value = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    application = models.ForeignKeyField(ContentType, on_delete=models.CASCADE)


class ModelModification(BaseModel):
    previously = models.ManyToManyField(ModelObject, null=True)
    currently = models.ManyToManyField(ModelObject, null=True)


class ModelChangelog(BaseModel):
    modification = models.OneToOneField(ModelModification, null=True)
    inserted = models.ManyToManyField(ModelObject, null=True)
    removed = models.ManyToManyField(ModelObject, null=True)

    information = models.OneToOneField(ModelObject)

    # def __str__(self):
    #     return_string = ''
    #     if self.modified_before is not None and self.modified_before != '':
    #         return_string += ' {0} changed to {1}; '.format(self.modified_before, self.modified_now)
    #     if self.added is not None and self.added != '':
    #         return_string += ' added {0}; '.format(self.added)
    #     if self.removed is not None and self.removed != '':
    #         return_string += ' removed {0}; '.format(self.removed)

    #     return return_string

    class Meta:
        verbose_name = "Model entry change"
        verbose_name_plural = "Model entry changes"


class Model(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    application = models.ForeignKeyField(ContentType, on_delete=models.CASCADE)

    message = models.TextField(null=True)

    MODES = (
        (0, 'n/a'),
        (1, 'add'),
        (2, 'change'),
        (3, 'delete'),
    )
    action = models.PositiveSmallIntegerField(choices=MODES, default=0)

    information = models.OneToOneField(ModelObject)
    modification = models.ForeignKey(ModelChangelog, null=True)

    def __str__(self):
        return '{0} - {1}'.format(self.date_created, self.message)

    class Meta:
        verbose_name = 'model log entry'
        verbose_name_plural = 'model log entries'


class Request(BaseModel):
    application = models.ForeignKeyField(ContentType, on_delete=models.CASCADE)

    # request = models.CharField(max_length=255)  # ??
    url = models.URLField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    def __str__(self):
        return '{2} - {0} performed request at {3} ({1})'.format(self.user, self.request, self.date_created, self.application)

    class Meta:
        verbose_name = "request event entry"
        verbose_name_plural = "request event entries"


class Unspecified(BaseModel):
    message = models.TextField(null=True)
    level = models.PositiveSmallIntegerField(default=20)

    file = models.CharField(max_length=255, null=True)
    line = models.PositiveIntegerField(null=True)

    def __str__(self):
        # conversion to python levels
        if self.level == 10:
            level = 'DEBUG'
        elif self.level == 20:
            level = 'INFO'
        elif self.level == 30:
            level = 'WARNING'
        elif self.level == 40:
            level = 'ERROR'
        elif self.level == 50:
            level = 'CRITICAL'
        else:
            level = 'NOTSET'

        return '{0} - {1} - {2} ({3} - {4})'.format(self.date_created, level, self.message, self.path, self.line)

    class Meta:
        verbose_name = " logging entry (Errors, Warnings, Info)"
        verbose_name_plural = " logging entries (Errors, Warnings, Info)"


class LDAP(BaseModel):

    class Meta:
        verbose_name = "LDAP event log entry"
        verbose_name_plural = "LDAP event log entries"

    action = models.TextField()
    succeeded = models.NullBooleanField(blank=True, null=True)
    errorMessage = models.TextField(blank=True, null=True)

    basedn = models.TextField(blank=True, null=True)
    entry = models.TextField(blank=True, null=True)

    objectClass = models.TextField(blank=True, null=True)
    cn = models.TextField(blank=True, null=True)

    existing_members = models.TextField(blank=True, null=True)
    data_members = models.TextField(blank=True, null=True)
    diff_members = models.TextField(blank=True, null=True)
