from django.core.files.storage import FileSystemStorage
from django.urls import reverse

from ..utils.helpers import parse_filename_to_args


class ImageStorage(FileSystemStorage):

    def url(self, name):
        return reverse('image_storage', args=parse_filename_to_args(name))
