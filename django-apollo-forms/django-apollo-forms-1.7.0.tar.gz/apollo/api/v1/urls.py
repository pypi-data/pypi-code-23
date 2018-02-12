from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from . import api_views


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'forms', api_views.FormViewSet)
router.register(r'submissions', api_views.FormSubmissionViewSet)
router.register(r'field-templates', api_views.FormFieldTemplateViewSet)
router.register(r'fields', api_views.FormFieldViewSet)
router.register(r'layouts', api_views.LayoutViewSet)

urlpatterns = router.urls

schema_view = get_swagger_view(title='Apollo API')

urlpatterns += (
    url(r'field-options/', api_views.FormFieldOptionsAPIView.as_view()),
    url(r'docs/', schema_view)
)