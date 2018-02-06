from django.conf.urls import url

from .views import (
    SingleLog,
    AllLogs,
    SingleRequestLog,
    AllRequestLogs,
    AllEventLogs,
    TestLogs,
    TestRequestLogs,
    TestEventLogs,
)

urlpatterns = [
    url(r'^(?P<log_id>[0-9]+)/$', SingleLog.as_view(), name='log'),
    url(r'^all/$', AllLogs.as_view(), name='all_logs'),
    url(r'^requests/(?P<log_id>[0-9]+)/$', SingleRequestLog.as_view(), name='request_log'),
    url(r'^requests/all/$', AllRequestLogs.as_view(), name='all_request_logs'),
    url(r'^events/all/$', AllEventLogs.as_view(), name='all_event_logs'),
    url(r'^test/$', TestLogs.as_view(), name='test'),
    url(r'^requests/test/$', TestRequestLogs.as_view(), name='request_test'),
    url(r'^events/test/$', TestEventLogs.as_view(), name='event_test'),
]
