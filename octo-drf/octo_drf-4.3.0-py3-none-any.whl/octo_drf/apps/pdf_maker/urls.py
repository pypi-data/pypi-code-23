


from rest_framework import routers

from .views import PDFViewSet


router = routers.DefaultRouter()
router.register('pdf_templates', PDFViewSet)

urlpatterns = []
urlpatterns += router.urls



