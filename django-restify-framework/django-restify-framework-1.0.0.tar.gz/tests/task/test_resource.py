# coding: utf-8

import json

from django.test import TestCase, RequestFactory

from restify.task import api_task
from restify.task.resource import TaskResource


class TaskResourceTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def tearDown(self):
        api_task._registry = {}

    def test_post_exception(self):
        resource = TaskResource.as_callable()

        request = self.rf.post('/')
        response = resource(request)
        self.assertEqual(response.status_code, 400)

        content = json.loads(response.content.decode())
        self.assertIn('Traceback', content['exception'])

    def post(self):
        @api_task(name='echo')
        def echo(*args, **kwargs):
            return args, kwargs

        resource = TaskResource.as_callable()

        request = self.rf.post('/')
        request.POST = {
            'function': 'echo',
            'args': ('arg0', ),
            'kwargs': {'kwarg0': 'value0'}
        }
        response = resource(request)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content, json.dumps({
            'return': [
                ['arg0'],
                {'kwarg0': 'value0'}
            ]
        }).encode())
