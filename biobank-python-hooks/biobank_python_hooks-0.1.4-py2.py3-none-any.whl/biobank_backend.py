"""
Manages interface with biobank system.
"""
import requests

from biobank.conf import settings
from django.contrib.auth.models import User


class BiobankBackend:
    def __init__(self):
        pass

    def authenticate(self, username=None, password=None, token=None):
        if not token:
            r = requests.post(settings.API_URL+'/users/me', auth={'bearer': token})
        else:
            r = requests.post(settings.API_URL+'/auth/login',
                              data={'username': username, 'password': password,
                                    'client_id': settings.CLIENT_ID})
            if r.status_code == requests.codes.ok:
                response = r.json()
                return self.authenticate(token=response.access_token)
        if r.status_code == requests.codes.ok:
            response = r.json()
            try:
                user = User.objects.get(username=response.results.data.username)
            except User.DoesNotExist:
                user = User(username=response.results.data.username)
                user.email = response.results.data.email
                user.save()
            return user
        return None
