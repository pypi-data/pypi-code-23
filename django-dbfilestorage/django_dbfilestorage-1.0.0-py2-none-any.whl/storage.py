from __future__ import absolute_import, print_function, unicode_literals

import base64
import mimetypes
import logging
import os

from django.db.transaction import atomic
from django.db.models import Q
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core.urlresolvers import reverse_lazy

from .models import DBFile

L = logging.getLogger(__name__)


def _get_object(param):
    return DBFile.objects.filter(name=param).first()


class DBFileStorage(Storage):
    """
        This is the Test Database file upload storage backend.
        This is used so that in our test database we always have uploaded
         files.

        To read more about how to set it up and configure it:
            https://docs.djangoproject.com/en/1.8/howto/custom-file-storage
    """

    def _open(self, name, mode='rb'):
        the_file = _get_object(name)
        return ContentFile(base64.b64decode(the_file.b64))

    @atomic
    def _save(self, name, content, max_length=None):
        """
           The save method does most of the 'magic'.
           It stores the contents of the file as a base64 string.
           It then takes the filename, and tries to get the mimetype from that
            (for rendering)
           Then it takes the md5 of the read file and uses that as the "unique"
           key to access the file.
           Then it checks if the file exists and if it doesn't, it will create
           the entry in the database.

           :param name: file name to save
           :param content: Content object, where content.file is bytes

           :return str: the name(md5) to look up the file by.
        """

        # TODO: Make this conditional better
        if hasattr(content.file, "read"):
            read_data = content.file.read()
            if not read_data:
                # If it's empty, try to seek once.
                content.file.seek(0)
                read_data = content.file.read()
        else:
            read_data = content.file

        b64 = base64.b64encode(read_data)

        # USE mimetypes.guess_type as an attempt at getting the content type.
        ct = mimetypes.guess_type(name)[0]

        # create the file, or just return name if the exact file already exists
        the_file = DBFile.objects.filter(name=name).first()
        if not the_file:
            DBFile.objects.create(
                name=name,
                content_type=ct,
                b64=b64)
        else:
            the_file.content_type=ct
            the_file.b64 = b64
            the_file.save()

        return name

    def get_available_name(self, name, max_length=None):
        return name

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        # name is the Pk, so it will be unique, deleting on the QS so
        # that it fails silently if the file doesn't exist.
        DBFile.objects.filter(name=name).delete()

    def exists(self, name):
        return DBFile.objects.filter(name=name).exists()

    def size(self, name):
        dbf = _get_object(name)
        return len(dbf.b64)

    def url(self, name):
        dbf = _get_object(name)
        if dbf:
            return reverse_lazy('dbstorage_file', args=(dbf.name,))
        return reverse_lazy('dbstorage_file', args=(name,))

    def modified_time(self, name):
        dbf = _get_object(name)
        return dbf.mtime

    def listdir(self, path):
        dirs = []  # this doesn't support dirs, so just empty list
        files = sorted(DBFile.objects.filter(
                    name__startswith=path
                ).values_list(
                    "name", flat=True
                ))
        return (dirs, files)
