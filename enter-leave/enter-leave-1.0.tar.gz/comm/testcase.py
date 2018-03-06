# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase, Client
import json
from django.conf import settings


class PublicBaseClass(TestCase):
    def operations(self, method='get', url=None, headers=None, status_code=200, params=None):
        if method == 'get':
            r = self.client.get(url)
        elif method == 'post':
            r = self.client.post(url, data=json.dumps(params), content_type='application/json')
        elif method == 'put':
            r = self.client.put(url, data=json.dumps(params), content_type='application/json')
        elif method == 'patch':
            r = self.client.patch(url, data=json.dumps(params), content_type='application/json')
        elif method == 'delete':
            r = self.client.delete(url)
        else:
            self.assertEqual(method, 'not supported')
        if r.status_code != status_code:
            print r.data
        self.assertEquals(r.status_code, status_code)
        return r

    def setUp(self):
        settings.USE_TZ = False
        self.client = Client()

    def tearDown(self):
        settings.USE_TZ = True
