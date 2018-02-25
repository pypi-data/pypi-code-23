from django.conf.urls import url

from .views import StatusView, DBStatusView

app_name = 'status'
urlpatterns = [
    url(r'^$', StatusView.as_view(), name='view'),
    url(r'^databases/$', DBStatusView.as_view(), name='view'),
]
