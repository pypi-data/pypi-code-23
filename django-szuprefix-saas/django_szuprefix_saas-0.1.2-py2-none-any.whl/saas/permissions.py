# -*- coding:utf-8 -*-
from rest_framework.permissions import BasePermission

__author__ = 'denishuang'

class IsSaasWorker(BasePermission):
    message = u"没有权限, 不是saas用户"

    def has_permission(self, request, view):
        return hasattr(request.user, "as_saas_worker")
