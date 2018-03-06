import datetime
from django.contrib.auth.models import User
from django.test import TestCase, Client
import json, requests
from django.conf import settings
from django.utils.timezone import utc

from . import models
from test_data import person_test_data
from django.utils import timezone
# Create your tests here.


class TestPersonEnterLeave(TestCase):
    def operations(self, method='get', url=None, headers=None, status_code=200, params=None):
        if method == 'get':
            r = self.client.get(url, HTTP_AUTHORIZATION=self.auth)
        elif method == 'post':
            r = self.client.post(url, data=json.dumps(params), content_type='application/json',
                                 HTTP_AUTHORIZATION=self.auth)
        elif method == 'put':
            r = self.client.put(url, data=json.dumps(params), content_type='application/json',
                                HTTP_AUTHORIZATION=self.auth)
        elif method == 'patch':
            r = self.client.patch(url, data=json.dumps(params), content_type='application/json',
                                  HTTP_AUTHORIZATION=self.auth)
        elif method == 'delete':
            r = self.client.delete(url, HTTP_AUTHORIZATION=self.auth)
        else:
            self.assertEqual(method, 'not supported')
        if r.status_code != status_code:
            print r.content
        self.assertEquals(r.status_code, status_code)
        return r

    def setUp(self):
        settings.USE_TZ = False
        user = User.objects.create(username="test")
        user.set_password('123456')
        user.is_staff = True
        user.save()
        self.client.login(username="test", password='123456')
        self.auth = requests.auth._basic_auth_str('test', '123456')
        self.client = Client()

        self.person = models.Person.objects.create(**person_test_data.test_enter_list_data.get('person'))
        self.enter = models.EnterOrLeave.objects.get(person=self.person)
        self.enter.enter_time = timezone.now()
        self.enter.create_on = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.enter.enter_status = 0
        self.enter.save()

    def tearDown(self):
        settings.USE_TZ = True

    def test_person_enter_list(self):
        r = self.operations(url=person_test_data.person_enter_url)
        self.assertEquals(r.data[0].get('enter_status'), 0)
        self.assertEquals(r.data[0].get('person').get('id_card'), person_test_data.test_enter_list_data.get(
            'person').get('id_card'))

    def test_person_enter_list_search(self):
        r = self.operations(url=person_test_data.person_enter_search_url)

    def test_person_enter_post(self):
        r = self.operations(url=person_test_data.person_enter_url, method=person_test_data.post_method,
                            params=person_test_data.test_enter_post_data, status_code=person_test_data.created_status)
        self.assertEquals(r.data.get('person').get('id_card'), person_test_data.test_enter_post_data.get(
            'person').get('id_card'))

    def test_person_enter_put(self):
        r = self.operations(url=person_test_data.person_enter_detail_url.format(pk=self.enter.pk),
                            method=person_test_data.put_method, params=person_test_data.test_enter_post_data)
        self.assertEquals(r.data.get('person').get('name'), person_test_data.test_enter_post_data.get(
            'person').get('name'))

    def test_person_enter_patch(self):
        r = self.operations(url=person_test_data.person_enter_detail_url.format(pk=self.enter.pk),
                            method=person_test_data.patch_method, params=person_test_data.test_enter_post_data)
        self.assertEquals(r.data.get('person').get('name'), person_test_data.test_enter_post_data.get(
            'person').get('name'))

    def test_person_enter_delete(self):
        self.operations(url=person_test_data.person_enter_detail_url.format(pk=self.enter.pk),
                        method=person_test_data.delete_method, status_code=person_test_data.delete_status)

    def test_person_leave(self):
        r = self.operations(url=person_test_data.person_leave_url.format(pk=self.enter.pk))
        self.assertEquals(len(r.data.get('history')), 1)
        self.assertEquals(r.data.get('enter_status'), 1)

    def test_person_enter_bulk(self):
        r = self.operations(url=person_test_data.person_enter_bulk_url, method=person_test_data.post_method,
                            status_code=person_test_data.created_status,
                            params=person_test_data.test_person_enter_bulk_data)
        self.assertEquals(len(r.data), len(person_test_data.test_person_enter_bulk_data))

    def test_enter_leave_calculation(self):
        r = self.operations(url=person_test_data.enter_leave_calculation_url.format(keyword='gender', status=0))
        r = self.operations(url=person_test_data.enter_leave_calculation_url.format(keyword='gender', status=1))
