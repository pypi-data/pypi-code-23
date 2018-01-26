from django.conf.urls import url

from .views import MySettingsView

view = MySettingsView.as_view()

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/pretix_mabel/settings',
        view, name='settings'),
]
