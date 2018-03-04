# -*- coding:utf-8 -*-
from rest_framework.authentication import SessionAuthentication as OrgSessionAuthentication
from django.core import urlresolvers

__author__ = 'denishuang'


class SessionAuthentication(OrgSessionAuthentication):
    def authenticate_header(self, request):
        return urlresolvers.reverse('login')
