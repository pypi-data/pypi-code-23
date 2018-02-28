from django.urls import reverse


def default_auth_handler(request):
    return {'url': reverse('login')}
