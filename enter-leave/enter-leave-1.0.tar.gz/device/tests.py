# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from datetime import datetime
from . import models
from .test_data import device_mobility
from comm.testcase import PublicBaseClass
# Create your tests here.


class TestDevice_mobilityViewCase(PublicBaseClass):
    @classmethod
    def setUpTestData(cls):
        cls.device = models.Device.objects.create(**device_mobility.device_test_data)
        cls.device_mobility = models.DeviceMobility.objects.create(**device_mobility.device_mobility_test_data)

    def test_device_get(self):
        r = self.operations(url=device_mobility.device_url)
        self.assertEquals(r.data[0].get('name'), device_mobility.device_test_data.get('name'))
        self.assertEquals(r.data[0].get('code'), device_mobility.device_test_data.get('code'))

    def test_device_post(self):
        r = self.operations(url=device_mobility.device_url, method=device_mobility.post_method,
                            params=device_mobility.device_post_data,
                            status_code=device_mobility.created_status_code)
        self.assertEquals(r.data.get('name'), device_mobility.device_post_data.get('name'))
        self.assertEquals(r.data.get('code'), device_mobility.device_post_data.get('code'))

    def test_device_detail(self):
        r = self.operations(url=device_mobility.device_operate_url.format(pk=self.device.id))
        self.assertEquals(r.data.get('name'), device_mobility.device_test_data.get("name"))
        self.assertEquals(r.data.get('code'), device_mobility.device_test_data.get("code"))

    def test_accident_type_put(self):
        r = self.operations(method=device_mobility.put_method, params=device_mobility.device_post_data,
                            url=device_mobility.device_operate_url.format(pk=self.device.id))
        self.assertEquals(r.data.get('name'), device_mobility.device_post_data.get('name'))
        self.assertEquals(r.data.get('code'), device_mobility.device_post_data.get('code'))

    def test_accident_type_patch(self):
        r = self.operations(method=device_mobility.patch_method, params=device_mobility.device_post_data,
                            url=device_mobility.device_operate_url.format(pk=self.device.id))
        self.assertEquals(r.data.get('name'), device_mobility.device_post_data.get('name'))
        self.assertEquals(r.data.get('code'), device_mobility.device_post_data.get('code'))

    def test_accident_type_delete(self):
        self.operations(method=device_mobility.delete_method, status_code=device_mobility.delete_status_code,
                        url=device_mobility.device_operate_url.format(pk=self.device.id))

    def test_device_mobility_post(self):
        r = self.operations(method=device_mobility.post_method, url=device_mobility.device_mobility_url,
                            params=device_mobility.device_mobility_post_data,
                            status_code=device_mobility.created_status_code)
        self.assertEquals(r.data.get('project'), device_mobility.device_mobility_post_data.get('project'))
        self.assertEquals(r.data.get('project_unit'),
                             device_mobility.device_mobility_post_data.get('project_unit'))

    def test_device_mobility_list(self):
        r = self.operations(url=device_mobility.device_mobility_url)
        self.assertEquals(r.data[0].get('project').get('pk'), device_mobility.device_mobility_test_data.get('project').get('pk'))
        self.assertEquals(r.data[0].get('project_unit').get('name'),
                          device_mobility.device_mobility_test_data.get('project_unit').get('name'))

    def test_device_mobility_detail(self):
        r = self.operations(url=device_mobility.device_mobility_operate_url.format(pk=self.device_mobility.id))
        self.assertEquals(r.data.get('project').get('pk'), device_mobility.device_mobility_test_data.get('project').get('pk'))
        self.assertEquals(r.data.get('images'), device_mobility.device_mobility_test_data.get('images'))

    def test_device_mobility_put(self):
        r = self.operations(url=device_mobility.device_mobility_operate_url.format(pk=self.device_mobility.id),
                            method=device_mobility.put_method,
                            params=device_mobility.device_mobility_post_data)
        self.assertEquals(r.data.get('project'), device_mobility.device_mobility_post_data.get('project'))
        self.assertEquals(r.data.get('images'), device_mobility.device_mobility_post_data.get('images'))

    def test_device_mobility_patch(self):
        r = self.operations(url=device_mobility.device_mobility_operate_url.format(pk=self.device_mobility.id),
                            method=device_mobility.patch_method,
                            params=device_mobility.device_mobility_post_data)
        self.assertEquals(r.data.get('project'), device_mobility.device_mobility_post_data.get('project'))
        self.assertEquals(r.data.get('snapshots1'), device_mobility.device_mobility_post_data.get('snapshots1'))

    def test_device_mobility_delete(self):
        self.operations(method=device_mobility.delete_method,
                        url=device_mobility.device_mobility_operate_url.format(pk=self.device_mobility.id),
                        status_code=device_mobility.delete_status_code)

    def test_device_mobility_search(self):
        r = self.operations(url=device_mobility.device_mobility_search_url.format(pro_pk=self.device_mobility.project.get('pk')))
        self.assertEquals(r.data[0].get('project').get('pk'), self.device_mobility.project.get('pk'))
        self.assertEquals(r.data[0].get('project').get('code'), device_mobility.device_mobility_test_data.get('project').get('code'))