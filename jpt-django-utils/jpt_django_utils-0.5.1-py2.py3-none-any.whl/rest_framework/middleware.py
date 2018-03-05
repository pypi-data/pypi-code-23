"""Util middlewares."""
import logging

from django.conf import settings
from django.http import JsonResponse


# Share same logger
logger = logging.getLogger('django.request')


class ExceptionMiddleware:
    """Jewel styled response for unhandled errors.

    Instead of returning a HTML response, return a Jewel styled JSON response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Return a JSON response for unhandled errors instead of HTML.

        If DEBUG is enabled, show a traceback instead.
        """
        if settings.DEBUG:
            return None

        logger.error(
            "Internal Server Error: {0}".format(request.path),
            exc_info=str(exception),
            extra={'status_code': 500, 'request': request}
        )

        return JsonResponse({
            "status_cd": "9999",
            "status_desc": "Server Error",
        }, status=500)
