# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase, Client
from .test_data import news
from . import models
import json
import unittest

# Create your tests here.
class PublicBaseClass(TestCase):
    def operations(self, method='get', url=None, headers=None, status_code=200, params=None):
        if method == 'get':
            res = self.client.get(url)
        elif method == 'post':
            res = self.client.post(url, data=json.dumps(params), content_type='application/json')
        elif method == 'put':
            res = self.client.put(url, data=json.dumps(params), content_type='application/json')
        elif method == 'patch':
            res = self.client.patch(url, data=json.dumps(params), content_type='application/json')
        elif method == 'delete':
            res = self.client.delete(url)
        else:
            self.assertEqual(method, 'not supposrted')
        return res
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

class TestNewsViewsCase(PublicBaseClass):
    @classmethod
    def setUpTestData(cls):
        cls.tag = models.Tag.objects.create(**news.tag_test_data)
        cls.category = models.Category.objects.create(**news.category_test_data)
    def test_tag_list(self):
        res = self.operations(url=news.tag_url)
        self.assertEquals(res.data[0].get('name'), '新闻')
    def test_tag_post(self):
        res = self.operations(url=news.tag_url, method=news.post_method, params=news.tag_post_data,
                              status_code=news.created_status_code)
        self.assertEquals(res.data['name'], '公告')
    def test_tag_detail(self):
        res = self.operations(url=news.tag_operate_url.format(pk=self.tag.id))
        self.assertEquals(res.data['name'], '新闻')
    def test_tag_put(self):
        res = self.operations(url=news.tag_operate_url.format(pk=self.tag.id), params=news.tag_post_data,
                              method=news.put_method)
        self.assertEquals(res.data['name'], '公告')
    def test_tag_delete(self):
        res = self.operations(url=news.tag_operate_url.format(pk=self.tag.id), method=news.delete_method,
                              status_code=news.delete_status_code)

    def test_category_list(self):
        res = self.operations(url=news.category_url)
        self.assertEquals(res.data[0].get('name'), '展示')
    def test_category_post(self):
        res = self.operations(url=news.category_url, method=news.post_method,params=news.category_post_data,
                              status_code=news.created_status_code)
        self.assertEquals(res.data['name'], '开发')
    def test_category_put(self):
        res = self.operations(url=news.category_operate_url.format(pk=self.category.id), params=news.category_post_data,
                              method=news.put_method)
        self.assertEquals(res.data['name'], '开发')
    def test_category_detail(self):
        res = self.operations(url=news.category_operate_url.format(pk=self.category.id))
        self.assertEquals(res.data['name'], '展示')
    def test_category_delete(self):
        res = self.operations(url=news.category_operate_url.format(pk=self.category.id), method=news.delete_method,
                              status_code=news.delete_status_code)




