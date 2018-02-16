# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ArticlesConfig(AppConfig):
    name = 'ripiu.cmsplugin_articles'
    verbose_name = _('Articles and sections')
