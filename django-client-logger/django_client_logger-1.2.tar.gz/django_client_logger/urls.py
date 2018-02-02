from django.conf.urls import url
from django_client_logger.views import LogReceiver


urlpatterns = [
    url(r'log', LogReceiver.as_view(), name='client_log_api')
]
