# -*- coding: utf-8 -*-
from django.conf import settings  # NOQA
from appconf import AppConf


class CmspluginFilerImageAppConf(AppConf):
    MODULE_NAME = 'Ri+'
    HEAD_CHILD_CLASSES = None
    MAIN_CHILD_CLASSES = None
    CLASSNAME = 'ripiu'
    TEMPLATES = []

    class Meta:
        prefix = 'ripiu_articles'
