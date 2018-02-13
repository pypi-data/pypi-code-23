from django.conf.urls import url

from . import views


app_name = 'djabberd'

urlpatterns = [
    url(r'^auth/$', views.AuthView.as_view(), name='auth'),
    url(r'^user/$', views.UserView.as_view(), name='user'),
    url(r'^roster/$', views.RosterView.as_view(), name='roster'),
    url(r'^archive/$', views.ArchiveView.as_view(), name='archive'),
]
