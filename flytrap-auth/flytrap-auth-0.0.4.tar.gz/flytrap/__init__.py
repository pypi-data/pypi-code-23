#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'flytrap.auth'
    verbose_name = '权限管理'


default_app_config = 'flytrap.auth.AuthConfig'
