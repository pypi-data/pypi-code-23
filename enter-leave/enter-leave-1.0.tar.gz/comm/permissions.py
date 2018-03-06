# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission
from rest_framework.compat import is_authenticated

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        from django.conf import settings

        if getattr(settings, 'ENABLE_PERMISSION') and settings.ENABLE_PERMISSION:
            perms_map = getattr(view, 'perms_map', {})
            perms = perms_map.get(request.method, [])
            return request.user and is_authenticated(request.user) \
                and request.user.has_perms(perms)
        else:
            return True
