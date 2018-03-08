# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models
import markdown2

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    abstract = models.TextField(null=True, blank=True)
    raw = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    content_html = models.TextField(null=True, blank=True)
    attachment = JSONField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    publisher = models.ForeignKey(User)
    is_draft = models.BooleanField(default=False)
    keyword = models.CharField(max_length=255, null=True, blank=True)
    cover = JSONField(blank=True, null=True)
    # 0: 平件 1: 加急 2: 特急
    degree = models.IntegerField(default=0)
    source = JSONField(blank=True, null=True)
    reserve_one = JSONField(blank=True, null=True)
    reserve_two = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.content_html = markdown2.markdown(
            self.raw,
            extras=['code-friendly', 'fenced-code-blocks']
        ).encode('utf-8')
        super(Post, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

class UserWebReadPost(models.Model):
    user = models.OneToOneField(User)
    web_read_post = models.ManyToManyField(Post)


class UserMobileReadPost(models.Model):
    user = models.OneToOneField(User)
    mobile_read_post = models.ManyToManyField(Post)

class UserReadPost(models.Model):
    user = models.OneToOneField(User)
    post_ids = models.ManyToManyField(Post)