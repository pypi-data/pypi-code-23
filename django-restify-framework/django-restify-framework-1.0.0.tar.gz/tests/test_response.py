from django.test import TestCase

from restify.http.response import ApiResponse
from restify.serializers import BaseSerializer
from restify.http import status


class ApiResponseTest(TestCase):
    def test_serializaton(self):
        data = {'example': 'data'}
        resp = ApiResponse(data)
        self.assertEqual(resp._status_code, status.HTTP_200_OK)
        django_resp = resp.to_django_response(serializer=BaseSerializer)
        self.assertEqual(django_resp.content, b'{\"example\": \"data\"}')