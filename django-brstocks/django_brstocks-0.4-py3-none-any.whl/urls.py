from django.conf.urls import url, include
from . import views as invest_views


urlpatterns = [
    url(r'^$', invest_views.index),
    
    url(r'^stocks/', invest_views.stocks, name='stocks'),
]
