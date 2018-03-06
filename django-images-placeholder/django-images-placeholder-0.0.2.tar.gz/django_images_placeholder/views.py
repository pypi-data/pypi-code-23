import urllib2

from PIL import Image, ImageFont, ImageDraw
from django.conf import settings
from django.core.cache import cache
from django.http import Http404, FileResponse
# TODO: Move this dependency to an isolated module, where a builtin `MediaSource` for `filer` will be implemented
from filer.fields.image import Image as ImageField
import os


def serve_image_placeholder(request):
    path = request.path_info
    image_path = path.replace('/media/', '')

    # TODO: Create mechanism to check `MediaSource`s instead os this bunch of `if`s and `try`s
    try:
        fpath = os.path.join(settings.BASE_DIR, path)
        with open(fpath, "rb") as f:
            return FileResponse(f, content_type="image/jpeg")

    except IOError:
        try:
            img_file = urllib2.urlopen(settings.ALTERNATIVE_MEDIA_URL + image_path)

        except urllib2.HTTPError as e:
            if e.code == 404 or e.code == 500:
                raise Http404("File not found.")

        try:
            file_name = settings.MEDIA_ROOT + '/' + image_path
            dirname = os.path.dirname(file_name)

            if not os.path.exists(dirname):
                os.makedirs(dirname)

            with open(file_name, "wb") as new_image_file:
                new_image_file.write(img_file.read())

            return FileResponse(open(file_name, 'rb'), content_type="image/jpeg")
        except Exception as e:
            print e

        raise Http404("File not found.")


        # # TODO: abstract database check to a implementation of a `MediaSource` interface. Make it optional and configurable
        # image_field = ImageField.objects.filter(file=image_path).first()
        #
        # if image_field:
        #     return_image = cache.get("{width}-{height}".format(width=image_field._width, height=image_field._height))
        #     if not return_image:
        #         return_image = generate_image(image_field._width, image_field._height)
        #         cache.add("{width}-{height}".format(width=image_field._width, height=image_field._height), return_image)
        #
        # else:
        #     # TODO: abstract remote check to a implementation of a `MediaSource` interface. Make it optional
        #     try:

                # return_image = cache.get(path)
                # if not return_image:
                #     # TODO: refactor url path join
                #     image_url = settings.ALTERNATIVE_MEDIA_URL + image_path
                #     return_image = urllib2.urlopen(image_url)
                #     return_image = return_image.read()
                #     cache.add(path, return_image)

                # except urllib2.HTTPError as e:
                #     if e.code == 404:
                #         raise Http404("File not found.")


def generate_image(width=300, height=300):
    # TODO: move this function for `utils.py`
    if width < height:
        font_size = width / 7
    else:
        font_size = height / 7

    # text and image
    image_text = "{width} x {height}".format(width=width, height=height)
    image_name = settings.MEDIA_ROOT + "/generated/{width}-{height}.png".format(width=width, height=height)
    image_dir = os.path.dirname(image_name)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # create image
    image_file = Image.new('RGBA', (width, height), color='rgb(220,220,220)')

    # create text
    draw = ImageDraw.Draw(image_file)
    # TODO: abstract font file path
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Bold.ttf", font_size)
    w, h = draw.textsize(image_text, font=fnt)
    draw.text(((width - w) / 2, (height - h) / 2), image_text, font=fnt, fill="black")

    # TODO: draw some borders

    # save image
    image_file.save(image_name, "PNG")

    with open(image_name, "rb") as f:
        return FileResponse(f, content_type="image/jpeg")
