import os

from django.conf import settings
from django.http import HttpResponse
from django.template import loader

from easy_thumbnails.files import get_thumbnailer


def index(request):
    template = loader.get_template('index.html')
    thumb_url = get_thumbnailer(settings.BASE_DIR +
                                '/pipinator/website/static/mountains-big.jpg')['thumb'].url

    context = {
        'thumb_filename': os.path.basename(thumb_url)
    }

    return HttpResponse(template.render(context, request))
