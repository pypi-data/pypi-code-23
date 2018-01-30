from django.conf.urls import url

from drf_api_actions.views import Views

urlpatterns = [
    url('^docs/', Views.docs_as_view()),
    url('^schema/', Views.schema_as_view()),
    url('^api.js', Views.api_js_as_view()),
]
