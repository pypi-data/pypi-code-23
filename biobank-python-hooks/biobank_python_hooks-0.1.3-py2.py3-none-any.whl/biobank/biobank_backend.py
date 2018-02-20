import requests

from biobank.conf import settings
from django.contrib.auth.models import User

class BiobankBackend:
    def authenticate(self, request, username=None, password=None):
        r = requests.post(settings.API_URL+'/auth/login', data= {'username': username, 'password' : password, 'client_id' : settings.CLIENT_ID})
    def authenticate(self, request, token):
        r = requests.post(settings.API_URL+'/users/me', auth= {'bearer': token})

        if (r.status_code == requests.code.ok) :
            response = r.json()
            try:
                user = User.objects.get(username=r.results.data.username)
            except: User.DoesNotExist:
                user = User(username=r.results.data.username)
                user.email = r.results.data.email
                user.save()
            return user
        return None    
