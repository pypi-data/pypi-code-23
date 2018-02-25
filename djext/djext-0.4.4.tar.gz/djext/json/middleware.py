from django.conf import settings
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from djext.http.exceptions import HttpError
from .http.response import JsonResponse, JsonResponseServerError


class JsonExceptionResponseMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        accept = request.META.get('HTTP_ACCEPT')
        if accept and accept == 'application/json':
            if isinstance(exception, HttpError):
                return JsonResponse(
                    status=exception.status_code, reason=exception.reason)
            elif not isinstance(exception, Http404) and not settings.DEBUG:
                return JsonResponseServerError()
