from django.conf import settings
from django.apps.registry import apps

from restify.authentication.base import Authentication
from restify.models import ApiKey


class ApiKeyAuthentication(Authentication):
    """
    Handles API key auth, in which a user provides a username & API key.
    """
    def _extract_credentials(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION', '')
        if authorization and authorization.lower().startswith('apikey '):
            auth_type, data = authorization.split()
            username, api_key = data.split(':', 1)
        else:
            data = getattr(request, request.method, 'GET')
            username = data.get('username')
            api_key = data.get('api_key')

        return username, api_key

    def _get_key(self, user, api_key):
        """
        Attempts to find the API key for the user.
        """
        try:
            ApiKey.objects.get(user=user, key=api_key)
        except ApiKey.DoesNotExist:
            return False

        return True

    def is_authenticated(self, request, **kwargs):
        """
        Finds the user and checks their API key.
        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """

        try:
            username, api_key = self._extract_credentials(request)
        except ValueError:
            return False

        if not username or not api_key:
            return False

        kls = apps.get_model(settings.AUTH_USER_MODEL)
        username_field = kls.USERNAME_FIELD

        try:
            lookup_kwargs = {username_field: username}
            user = kls.objects.get(**lookup_kwargs)
        except (kls.DoesNotExist, kls.MultipleObjectsReturned):
            return False

        if not self.check_active(user):
            return False

        key_auth_check = self._get_key(user, api_key)
        if key_auth_check:
            request.user = user

        return key_auth_check