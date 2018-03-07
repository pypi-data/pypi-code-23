from django.test import TestCase
from django.test import RequestFactory
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse

from restify.resource import Resource
from restify.http.response import ApiResponse


class Resource1(Resource):
    def get(self, request, *args, **kwargs):
        return HttpResponse('')


class Resource2(Resource):
    def common(self, request, value):
        if value == 3:
            return HttpResponseNotFound('')
        self.request.example_value = '123'

    def get(self, request, value):
        return HttpResponse(self.request.example_value)


class Resource3(Resource):
    def get(self, request):
        data = {'asdf': 'asdf'}
        return ApiResponse(data)


class ResourceTest(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_init_and_call(self):
        """
        Only user-defined methods are callable (dispatch to the right method).
        """
        resource = Resource1.as_callable()

        request = self.rf.get('/')
        response = resource(request)
        ## get method is implemented, and returns response object
        self.assertEqual(response.status_code, 200)

        request = self.rf.post('/')
        response = resource(request)
        ## post method isn't implemented, so it isn't callable
        self.assertEqual(response.status_code, 405)

    def test_preprocess_request(self):
        """
        Call common method before run the "view" (get/post/etc... methods). If the pre-process
        raises an error, then return with 404 error page.
        """
        resource = Resource2.as_callable()

        request = self.rf.get('/')
        response = resource(request, value=1)
        self.assertEqual(response.content, b'123')
        self.assertEqual(response.status_code, 200)

        request = self.rf.get('/')
        response = resource(request, value=3)
        self.assertEqual(response.status_code, 404)

    def test_serializer(self):
        """
        If not HttpResponse returned, then create ApiResponse object.
        """
        resource = Resource3.as_callable()

        request = self.rf.get('/')
        response = resource(request)
        self.assertIsInstance(response, JsonResponse)