import http

from django.conf import settings
from django.http import HttpResponse

from sigauth.utils import RequestSignatureChecker


class SignatureCheckMiddlewareBase:

    secret = None
    request_checker = None

    def __init__(self, *args, **kwargs):
        assert self.secret, "subclass this and and set the `secret` property"
        self.request_checker = RequestSignatureChecker(self.secret)
        super().__init__(*args, **kwargs)

    def process_request(self, request):
        if request.path not in settings.URLS_EXCLUDED_FROM_SIGNATURE_CHECK:
            if not self.request_checker.test_signature(request):
                return HttpResponse(
                    'Unauthorized', status=http.client.UNAUTHORIZED.value
                )
