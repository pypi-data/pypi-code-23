from django.conf.urls import url, include
from rest_framework import routers

from location.views import CityViewSet, StateViewSet, CountryViewSet, CountryCodeViewSet

router = routers.DefaultRouter()
router.register(r'Cities', CityViewSet)
router.register(r'States', StateViewSet)
router.register(r'Countries', CountryViewSet)
router.register(r'CountriesCodes', CountryCodeViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]