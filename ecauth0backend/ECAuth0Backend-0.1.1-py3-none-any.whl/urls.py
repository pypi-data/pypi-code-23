from django.conf.urls import url
from ECAuth0Backend import views
from ECAuth0Backend.settings import AUTH0_BACKEND_CALLBACK_URL

urlpatterns = [
    url(AUTH0_BACKEND_CALLBACK_URL, views.auth_callback, name='auth_callback'),
]
