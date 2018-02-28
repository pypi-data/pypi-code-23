import os

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status
from rest_framework import views, generics
from rest_framework.response import Response
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.parsers import ThumbnailParseError

from .models import GenericImage
from .serializers import GenericImageSerializer


class ImageStorageView(views.APIView):
    #TODO написать докстринг

    def get(self, *args, **kwargs):

        app = kwargs.get('app')
        model = kwargs.get('model')
        field = kwargs.get('field')
        uuid4 = kwargs.get('uuid4')
        ext = kwargs.get('ext')
        geometry = kwargs.get('geometry')
        crop = kwargs.get('crop')
        upscale = kwargs.get('upscale')

        actual_model = apps.get_model(app, model)

        try:
            name = os.path.join(
                'images', app, model, field, uuid4 + '.' + ext)
            image_model = actual_model.objects.get(**{field: name})
            image = getattr(image_model, field)
        except ObjectDoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)

        if any((geometry, crop, bool(upscale))):
            ext = 'PNG' if ext == 'png' else 'JPEG'
            upscale = 'True' if not upscale else False
            try:
                thumb = get_thumbnail(
                    image, geometry, crop=crop,
                    upscale=upscale, format=ext)
                media = settings.MEDIA_ROOT[:settings.MEDIA_ROOT.find('/media')]
                f = open(media + thumb.url, 'rb')
            except (ValueError, TypeError, ThumbnailParseError):
                f = open(image.path, 'rb')
        else:
            f = open(image.path, 'rb')
        content = f.read()
        content_type = 'image/png' if ext == 'PNG' else 'image/jpg'
        f.close()

        response = HttpResponse(content, content_type=content_type)
        response['Cache-Control'] = 'max-age={days}'.format(days=360)
        return response


class ImageUploadView(generics.CreateAPIView):

    serializer_class = GenericImageSerializer
    queryset = GenericImage
