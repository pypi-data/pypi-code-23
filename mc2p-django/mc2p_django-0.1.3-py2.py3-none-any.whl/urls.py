from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^notify/$', views.MC2PNotifyView.as_view(), name='mc2p-notify'),
]
