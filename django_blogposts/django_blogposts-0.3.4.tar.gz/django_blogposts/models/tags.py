# -*- coding: utf-8 -*-
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
__author__ = "spi4ka"


class Tags(models.Model):

    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(
        _("Slug"),
        max_length=200,
        allow_unicode=True
    )

    is_moderated = models.BooleanField(_("Is moderated"), default=True)

    da = models.DateTimeField(_("Date of create"), auto_now_add=True)
    de = models.DateTimeField(_("Date of last edit"), auto_now=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['-da']

    def __unicode__(self):
        return u"{}".format(self.__str__(),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('django-blogposts-list') + "?tag=%s" % (self.slug, )
