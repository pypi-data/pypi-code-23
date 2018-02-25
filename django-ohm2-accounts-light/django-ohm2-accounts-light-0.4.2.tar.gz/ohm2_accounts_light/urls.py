from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (2, 0):
	from django.urls import include, re_path as url
else:
	from django.conf.urls import include, url

from . import views

app_name = "ohm2_accounts_light"

urlpatterns = [
	url(r'^api/v1/', include('ohm2_accounts_light.api.v1.urls', namespace = "api_v1")),
]

