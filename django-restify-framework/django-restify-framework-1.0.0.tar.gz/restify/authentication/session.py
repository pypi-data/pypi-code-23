from .base import Authentication


class DjangoAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if not hasattr(request, 'user'):
            return False
        return request.user.is_authenticated

