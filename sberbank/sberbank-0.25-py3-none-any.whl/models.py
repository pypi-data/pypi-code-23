import uuid
from enum import IntEnum

from django.db import models
from django.contrib.postgres.fields import JSONField


class Choisable(IntEnum):
    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class Status(Choisable):
    CREATED = 0
    PENDING = 1
    SUCCEEDED = 2
    FAILED = 3

    def __str__(self):
        return str(self.value)


class Payment(models.Model):
    """
    details JSON fields:
        username
        currency
        success_url
        fail_url
        session_timeout
        page_view
        redirect_url
    """

    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    bank_id = models.UUIDField(null=True)
    amount = models.DecimalField(max_digits=128, decimal_places=2)
    error_code = models.PositiveIntegerField(null=True)
    error_message = models.TextField(null=True)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices(),
        default=Status.CREATED)
    details = JSONField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class LogType(Choisable):
    CREATE = 0
    CALLBACK = 1
    CHECK_STATUS = 2

    def __str__(self):
        return str(self.value)


class BankLog(models.Model):
    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    payment_id = models.UUIDField(null=True)
    bank_id = models.UUIDField(null=True)
    request_type = models.CharField(
        max_length=1,
        choices=LogType.choices())
    response_json = JSONField(blank=True, null=True)
    response_text = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
