#!/usr/bin/env python
# -*- coding:utf-8 -*-
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


# 消息
class Message(models.Model):
    name = models.CharField(max_length=180, verbose_name='消息名称')
    info = models.CharField(max_length=180, null=True,blank=True, verbose_name='说明')
    is_user_show = models.BooleanField(default=False, verbose_name="学生页是否显示")
    is_admin_show = models.BooleanField(default=False, verbose_name="管理页是否显示")

    class Meta:
        db_table = 'bee_django_message'
        ordering = ["id"]

    def __unicode__(self):
        return ("Message->name:" + self.name)

    def get_absolute_url(self):
        return reverse('bee_django_message:message_list')

    def get_user_show(self):
        if self.is_user_show:
            return "是"
        else:
            return '否'

    def get_admin_show(self):
        if self.is_admin_show:
            return "是"
        else:
            return '否'


class SendRecord(models.Model):
    from_user = models.ForeignKey(get_user_table(), related_name='bee_message_from_user', verbose_name='来自',null=True)
    to_user = models.ForeignKey(get_user_table(), related_name='bee_message_to_user', verbose_name='发送给')
    message = models.ForeignKey('bee_django_message.Message', related_name='record_message',null=True)
    title = models.CharField(max_length=180, verbose_name='主题')
    info = models.CharField(max_length=180, null=True, verbose_name='内容', blank=True)
    is_view = models.BooleanField(default=False, verbose_name='是否看过')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    url = models.CharField(max_length=180, null=True, verbose_name='点击后跳转到的页面')

    class Meta:
        db_table = 'bee_django_message_record'
        ordering = ["-sent_at"]

    def __unicode__(self):
        return ("SendRecord->title:" + self.title)

    def get_absolute_url(self):
        return reverse('bee_django_message:record_list')
