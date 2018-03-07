import uuid
from enum import IntEnum

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext as _


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
    bank_id = models.UUIDField(_("Идентификатор банка"),
                               null=True, blank=True)
    amount = models.DecimalField(_("Сумма платежа"),
                                 max_digits=128, decimal_places=2)
    error_code = models.PositiveIntegerField(_("Код ошибки банка"),
                                             null=True, blank=True)
    error_message = models.TextField(_("Описание ошибки банка"),
                                     null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        _("Статус платежа"),
        choices=Status.choices(),
        default=Status.CREATED)
    details = JSONField(_("Детали платежа"),
                        blank=True, null=True)
    created = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        ordering = ['-updated']
        verbose_name = _('платеж')
        verbose_name_plural = _('платежи')


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
    payment_id = models.UUIDField(_("Идентификатор платежа"),
                                  null=True, blank=True)
    bank_id = models.UUIDField(_("Идентификатор платежа банка"),
                               null=True, blank=True)
    request_type = models.CharField(
        _("Тип запроса"),
        max_length=1,
        choices=LogType.choices())
    response_json = JSONField(_("Ответ банка(json)"),
                              blank=True, null=True)
    response_text = models.TextField(_("Ответ банка"), null=True, blank=True)
    created = models.DateTimeField(_("Создано"), auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('лог сообщений')
        verbose_name_plural = _('лог сообщений')
