from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from .settings import apollo_settings
from .views import FormManager, DownloadFormSubmissions, NoScriptForm
from .api import urls as api_urls
import os


form_builder_view = FormManager.as_view()
if apollo_settings.BUILDER_REQUIRES_IS_STAFF:
    form_builder_view = staff_member_required(form_builder_view)

download_submissions_view = DownloadFormSubmissions.as_view()
if apollo_settings.DOWNLOAD_REQUIRES_IS_STAFF:
    download_submissions_view = staff_member_required(download_submissions_view)

urlpatterns = [
    url(r'builder/', form_builder_view),
    url(r'download/', download_submissions_view),
    url(r'render/', NoScriptForm.as_view()),
    url(r'%s/' % os.path.join(apollo_settings.API_ROOT, apollo_settings.API_VERSION), include(api_urls))
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()