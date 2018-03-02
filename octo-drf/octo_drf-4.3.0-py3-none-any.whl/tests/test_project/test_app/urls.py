


from rest_framework import routers

from .views import CatalogItemViewSet, CatalogCategoryViewSet


router = routers.DefaultRouter()
router.register('catalog_items', CatalogItemViewSet, base_name='catalog_items')
router.register('catalog_categories', CatalogCategoryViewSet, base_name='catalog_categories')

urlpatterns = []
urlpatterns += router.urls
