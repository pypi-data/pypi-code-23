
from django.conf.urls import include, url

urlpatterns = [
    url(r'^auth/', include('octo_drf.apps.auth.urls')),
    url(r'^', include('octo_drf.apps.generic_image.urls')),
    url(r'^', include('octo_drf.apps.base_forms.urls')),
    url(r'^', include('octo_drf.apps.pdf_maker.urls'))
]
