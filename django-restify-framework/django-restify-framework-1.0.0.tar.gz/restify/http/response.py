#encoding: utf8
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from restify.http import status


class ApiResponse(object):
    def __init__(self, data, status_code=status.HTTP_200_OK, content_type='application/json'):
        self._data = data
        self._status_code = status_code
        self._content_type = content_type

    def to_django_response(self, serializer):
        if isinstance(serializer, type):
            serializer = serializer()

        serialized = serializer.flatten(self._data)
        if self._content_type == 'application/json':
            resp = JsonResponse(serialized, encoder=DjangoJSONEncoder, safe=False)
            resp.status_code = self._status_code
            return resp