from django.http import HttpResponse

from restify.http import status


class Authorization(object):
    def __init__(self, **kwargs):
        self._permissions = kwargs

    def unauthorized(self):
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    def has_perm(self, user, http_method):
        raise NotImplementedError