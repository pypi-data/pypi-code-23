from django.http import HttpResponse

from restify.http import status


class Authentication(object):
    def __init__(self, require_active=True):
        self.require_active = require_active

    def unauthorized(self):
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    def is_authenticated(self, request, **kwargs):
        raise NotImplementedError('Implement in subclass')

    def check_active(self, user):
        """
        Ensures the user has an active account.
        Optimized for the ``django.contrib.auth.models.User`` case.
        """
        if not self.require_active:
            # Ignore & move on.
            return True

        return user.is_active