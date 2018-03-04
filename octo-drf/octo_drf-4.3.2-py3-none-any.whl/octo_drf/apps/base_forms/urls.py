


from rest_framework import routers

from .views import FormMetaView


router = routers.DefaultRouter()
router.register('forms_meta', FormMetaView)

urlpatterns = []

urlpatterns += router.urls