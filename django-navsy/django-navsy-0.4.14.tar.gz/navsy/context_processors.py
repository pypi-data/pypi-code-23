# -*- coding: utf-8 -*-

from django.conf import settings


def data(request):
    d = {}
    d['navsy_debug'] = settings.DEBUG
    if request:
        d['navsy_host'] = '%s://%s' % (request.scheme, request.get_host(), )
        d.update(getattr(request, 'navsy_data', {}))
    return d
