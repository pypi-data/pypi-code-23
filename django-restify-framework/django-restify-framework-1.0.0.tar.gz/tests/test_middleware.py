import json

from django.test import TestCase, RequestFactory

from restify.http import status
from restify.middleware import PostInBodyMiddleware


class PostInBodyMiddlewareTest(TestCase):
    def _create_request(self, post_str):
        factory = RequestFactory()
        extra = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        request = factory.post('/', data=post_str,
                                    content_type='application/json',
                                    **extra)

        return request

    def test_data_in_body(self):
        post = {
            "columns": [
                {"key": "first", "value": "First column"}
            ],
            "limit": 10,
            "boolean": True
        }

        request = self._create_request(json.dumps(post))

        middleware = PostInBodyMiddleware()
        middleware.process_request(request)

        self.assertEqual(request.POST, post)

    def test_wrong_data(self):
        request = self._create_request("asdf")

        middleware = PostInBodyMiddleware()
        resp = middleware.process_request(request)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)