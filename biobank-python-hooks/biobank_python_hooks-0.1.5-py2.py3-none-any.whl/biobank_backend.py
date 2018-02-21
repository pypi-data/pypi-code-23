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
            r = requests.post(settings.API_URL + '/oauth/token',
                              data={'username': username, 'password': password,
                                    'client_id': settings.CLIENT_ID,
                                    'client_secret': settings.CLIENT_SECRET,
                                    'grant_type': settings.CLIENT_GRANT,
                                    })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return self.authenticate(token=response['access_token'])
        else:
            headers = {'Authorization': 'Bearer {}'.format(token)}
            r = requests.get(settings.API_URL + '/users/me', headers=headers)
        if r.status_code == requests.codes.ok:
            response = r.json()
            try:
                user = User.objects.get(username=response['results']['data']['email'])
            except User.DoesNotExist:
                person = response['results']['data']
                user = User(username=person['email'])
                user.first_name = person['firstName']
                user.last_name = person['lastName']
                user.email = person['email']
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
