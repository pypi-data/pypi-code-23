from django.conf.urls import url
from sberbank import views

urlpatterns = [
    url('payment/callback', views.callback)
]
