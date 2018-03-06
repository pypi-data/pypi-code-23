from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'api/person-enter/$', views.EnterListView.as_view()),
    url(r'api/person-enter/(?P<pk>[0-9]+)/$', views.EnterDetailView.as_view()),
    url(r'api/person-leave/(?P<pk>[0-9]+)/$', views.PersonLeaveView.as_view()),
    url(r'api/person-enter/bulk/$', views.PersonEnterBulkView.as_view()),
    url(r'api/enter-leave/calculation/', views.PersonEnterLeaveCalculation.as_view()),
]
