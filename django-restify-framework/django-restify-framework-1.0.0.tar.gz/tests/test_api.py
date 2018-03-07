from django.test import TestCase
from django.urls import URLPattern

from restify.api import Api
from restify.resource import Resource


class CustomResource(Resource):
    class Meta:
        resource_name = 'example'


class ApiTest(TestCase):
    def test_api_naming(self):
        api = Api()
        self.assertEqual(api.name, 'v1')
        api = Api(api_name='v2')
        self.assertEqual(api.name, 'v2')

    def test_api_urls_empty(self):
        api = Api()
        self.assertEqual(len(api.urls), 0)
        self.assertIsInstance(api.urls, list)

    def test_api_register_resource(self):
        api = Api()
        api.register(r'first/$', CustomResource)
        self.assertEqual(len(api.urls), 1)
        self.assertIsInstance(api.urls[0], URLPattern)
        self.assertEqual(api.urls[0].name, 'example')
