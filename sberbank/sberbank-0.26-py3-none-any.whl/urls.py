from django.conf.urls import url
from sberbank import views

urlpatterns = [  # noqa: pylint=invalid-name
    url('payment/callback', views.callback)
]
