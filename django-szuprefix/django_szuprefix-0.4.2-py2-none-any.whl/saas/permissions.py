# -*- coding:utf-8 -*-
from rest_framework.permissions import BasePermission

__author__ = 'denishuang'

class IsSaasWorker(BasePermission):

    def has_permission(self, request, view):
        return hasattr(request.user, "as_saas_worker")
