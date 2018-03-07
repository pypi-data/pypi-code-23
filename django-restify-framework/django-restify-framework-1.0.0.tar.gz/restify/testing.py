import json

from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.urls import reverse

from restify.authentication import ApiKeyAuthentication


class ApiTestMixin(object):
    def _parse_response(self, response):
        if response['Content-Type'] == 'application/json':
            response.json = json.loads(response.content.decode('utf8'))

        return response


class ApiTestCase(TestCase, ApiTestMixin):
    RESOURCE = None

    def _set_auth_data(self, request, **kwargs):
        if isinstance(self.RESOURCE.authentication, ApiKeyAuthentication):
            request.GET['username'] = kwargs['user'].username
            request.GET['api_key'] = kwargs['user'].api_key.key

    def _get_response(self, method_name, data, user, **extra):
        rfactory = RequestFactory()

        try:
            resource_url = reverse('api:{0}'.format(self.RESOURCE._meta.resource_name))
        except AttributeError: #AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'
            resource_url = '/'

        method = getattr(rfactory, method_name)
        request = method(resource_url, data, **extra)
        request.session = {}
        setattr(request, method_name.upper(), data)

        if user:
            self._set_auth_data(request, user=user)

        resource = self.RESOURCE()
        resource.request = request
        resp = resource(request, **extra)

        return self._parse_response(resp)

    def post(self, data, user=None, **extra):
        return self._get_response('post', data, user, **extra)

    def get(self, query={}, user=None, **extra):
        return self._get_response('get', data=query, user=user, **extra)


class LiveApiTestCase(LiveServerTestCase, ApiTestMixin):
    RESOURCE = None

    def _get_response(self, method_name, url, data=None):
        method = getattr(self.client, method_name)

        if method_name in ('post', 'put', 'POST', 'PUT'):
            data = json.dumps(data)

        return method(url, data=data, content_type='application/json; charset=utf-8')

    def get(self, data=None, **kwargs):
        reverse_name = "api:{}".format(self.RESOURCE.Meta.resource_name)
        url = reverse(reverse_name, kwargs=kwargs)
        resp = self._get_response('get', url=url, data=data)
        return self._parse_response(resp)

    def post(self, data=None, content_type='application/json', **kwargs):
        reverse_name = "api:{}".format(self.RESOURCE.Meta.resource_name)
        url = reverse(reverse_name, kwargs=kwargs)
        resp = self._get_response('post', url=url, data=data)
        return self._parse_response(resp)

    def put(self, data=None, **kwargs):
        reverse_name = "api:{}".format(self.RESOURCE.Meta.resource_name)
        url = reverse(reverse_name, kwargs=kwargs)
        resp = self._get_response('put', url=url, data=json.dumps(data))
        return self._parse_response(resp)
