# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.
def get_user_table():
    if settings.MESSAGE_USER_TABLE in ["", None]:
        user_table = User
    else:
        user_table = settings.MESSAGE_USER_TABLE
    return user_table

# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, settings.COIN_USER_NAME_FIELD)
    except:
        return None

class CoinType(models.Model):
    name = models.CharField(max_length=180, verbose_name='名称类型')
    coin = models.IntegerField(verbose_name="数量")
    info = models.CharField(max_length=180, null=True, blank=True, verbose_name='说明')
    identity=models.CharField(max_length=180,null=True,verbose_name='标识符',unique=True)


    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_type'
        ordering = ["id"]

    def __unicode__(self):
        return ("CoinType->name:" + self.name)

    def get_absolute_url(self):
        return reverse('bee_django_coin:coin_type_list')


# 缦币
class UserCoinRecord(models.Model):
    user = models.ForeignKey(get_user_table(), related_name='coin_user')
    coin = models.IntegerField(verbose_name='数量')
    created_by = models.ForeignKey(get_user_table(), related_name="created_by_user", null=True)
    reason = models.CharField(max_length=180, verbose_name='原因', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    coin_type = models.ForeignKey('bee_django_coin.CoinType', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_record'
        ordering = ["-created_at"]

    def __unicode__(self):
        return ("UserCoinRecord->reason:" + self.reason)

    def get_absolute_url(self):
        return reverse('bee_django_coin:user_coin_record')

    def get_created_by_user_name(self):
        if self.created_by:
            return get_user_name(self.created_by)
        else:
            return settings.COIN_DEFAULT_NAME
