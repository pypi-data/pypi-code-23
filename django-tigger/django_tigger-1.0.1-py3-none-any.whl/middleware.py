from django.contrib import messages
from django.http import HttpResponseRedirect

from .exceptions import Bounce


class BouncingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Bounce):
            if exception.message:
                messages.add_message(
                    request,
                    exception.level,
                    exception.message
                )
            return HttpResponseRedirect(exception.url)
