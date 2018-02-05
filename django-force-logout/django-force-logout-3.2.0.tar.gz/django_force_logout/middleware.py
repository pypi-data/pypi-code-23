import time
import django
import datetime

from django.contrib import auth
from django.utils.module_loading import import_string

from . import app_settings


if django.VERSION > (1, 10):
    from django.utils.deprecation import MiddlewareMixin

    def is_authenticated(user):
        return user.is_authenticated
else:
    MiddlewareMixin = object

    def is_authenticated(user):
        return user.is_authenticated()


class ForceLogoutMiddleware(MiddlewareMixin):
    SESSION_KEY = 'force-logout:last-login'

    def __init__(self, get_response=None):
        self.fn = app_settings.CALLBACK

        if not callable(self.fn):
            self.fn = import_string(self.fn)

        def callback(sender, user=None, request=None, **kwargs):
            if request:
                request.session[self.SESSION_KEY] = int(time.time())
        auth.signals.user_logged_in.connect(callback, weak=False)

    def process_request(self, request):
        if not is_authenticated(request.user):
            return

        user_timestamp = self.fn(request.user)

        if user_timestamp is None:
            return

        try:
            timestamp = datetime.datetime.utcfromtimestamp(
                request.session[self.SESSION_KEY],
            )
        except KeyError:
            # May not have logged in since we started populating this key.
            return

        if timestamp > user_timestamp:
            return

        auth.logout(request)
