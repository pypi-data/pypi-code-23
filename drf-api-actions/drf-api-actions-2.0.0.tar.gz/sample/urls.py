from django.conf.urls import include, url

from sample import settings
from sample.views import UsersAPIView, UsersActionReadAPIView, UsersExtraFieldsAPIView, InvitationAPIView

urlpatterns = [
    url('^api/', include([
        url('users/', include([
            url('^$', UsersAPIView.as_view()),
            url('^invitation$', InvitationAPIView.as_view()),
        ])),
        url('^users_action_read$', UsersActionReadAPIView.as_view()),
        url('^users_extra_fields/$', UsersExtraFieldsAPIView.as_view()),
    ])),
]

if settings.DEBUG:
    urlpatterns += [
        url('^', include('drf_api_actions.urls'))
    ]
