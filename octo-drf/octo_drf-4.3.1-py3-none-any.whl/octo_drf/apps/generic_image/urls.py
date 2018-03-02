from django.conf.urls import url

from .views import ImageStorageView, ImageUploadView

image_storage_view = ImageStorageView.as_view()
image_upload_view = ImageUploadView.as_view()

urlpatterns = [
    url(r'^storage/(?P<app>.+)/'
        r'(?P<model>.+)/'
        r'(?P<field>.+)/'
        r'(?P<uuid4>[0-9a-f-]+)'
        r'(_(?P<upscale>upscale))?'
        r'(_(?P<geometry>[x0-9]+))?'
        r'(_(?P<crop>.+))?'
        r'\.(?P<ext>[a-z]+)',
        image_storage_view,
        name='image_storage'
        ),

    url(r'^image_upload/', image_upload_view, name='upload_image'),
]
