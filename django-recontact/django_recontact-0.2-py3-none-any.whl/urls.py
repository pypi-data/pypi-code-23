from django.conf.urls import url
from .views import RecontactView

urlpatterns = [
    url(r'^$', RecontactView.as_view(), name='recontact_base'),
    url(r'^(?P<sent>sent)/$', RecontactView.as_view(), name='recontact_sent'),

]
