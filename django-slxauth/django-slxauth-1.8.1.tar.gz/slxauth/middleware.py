import re

from django.contrib.auth import logout
from django.utils import translation

from slxauth.utils import get_authenticator


class TokenAuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        access_token = None

        if 'HTTP_AUTHORIZATION' in request.META:
            m = re.search('Bearer (\\S+)', request.META['HTTP_AUTHORIZATION'])
            if m:
                access_token = m.group(1)
        else:
            access_token = request.COOKIES.get('access_token')
            #expiration_time = request.COOKIES.get('expiration_time')
            #refresh_token = request.COOKIES.get('refresh_token')

        if access_token:
            # update user from fresh token if needed
            if not request.user.is_authenticated or access_token != request.user.access_token:
                auth = get_authenticator()
                auth.login_using_token(request, access_token)
        else:
            # logout only access_token based users to keep django-admin login intact
            if request.user.is_authenticated and request.user.access_token:
                logout(request)

        # set language from profile
        if request.user.is_authenticated and request.user.language:
            translation.activate(request.user.language)
            request.session[translation.LANGUAGE_SESSION_KEY] = request.user.language

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
