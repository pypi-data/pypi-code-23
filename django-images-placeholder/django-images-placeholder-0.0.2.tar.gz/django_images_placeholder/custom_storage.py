import urllib2
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage
from django.http import Http404


class OverwritingStorage(FileSystemStorage):
    """
    File storage that allows overwriting of stored files.
    """

    VALID_IMAGE_EXTENSIONS = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
    ]

    def get_available_name(self, name):
        return name

    def valid_url_extension(self, url, extension_list=VALID_IMAGE_EXTENSIONS):
        for ext in extension_list:
            if url.endswith(ext):
                return ext
        return None

    def open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """
        try:
            return self._open(name, mode)
        except:
            if self.valid_url_extension(name) is not None:
                try:
                    img_file = urllib2.urlopen(settings.ALTERNATIVE_MEDIA_URL + name)

                except urllib2.HTTPError as e:
                    if e.code == 404 or e.code == 500:
                        return None

                try:
                    file_name = settings.MEDIA_ROOT + '/' + name
                    dirname = os.path.dirname(file_name)

                    if not os.path.exists(dirname):
                        os.makedirs(dirname)

                    new_image_file = open(file_name, "wb+")
                    new_image_file.write(img_file.read())
                    new_image_file.close()

                    return self._open(name, mode)

                except:
                    return None