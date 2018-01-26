
from django.db import models
from pretix.base.models.event import Event
from pretix.base.models.items import Item


class UserVouchers(models.Model):
    user = models.CharField(max_length=128, unique=True)
    voucher = models.CharField(max_length=20, unique=True)


class MabelSettings(models.Model):
    user_sheet_url = models.CharField(max_length=1024)


class TicketLimit(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        unique=True
    )
    current_student_limit = models.IntegerField()
    alumnus_limit = models.IntegerField()
    external_limit = models.IntegerField()
