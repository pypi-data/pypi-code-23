from __future__ import absolute_import, print_function, unicode_literals

from django.db import models
from future.utils import python_2_unicode_compatible


@python_2_unicode_compatible
class DBFile(models.Model):
    """ Model to store and access uploaded files """

    name = models.CharField(max_length=190, unique=True)

    # file data
    content_type = models.CharField(max_length=100)
    b64 = models.TextField()
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u"{name} <{content_type}>".format(
            name=self.name, content_type=self.content_type)

    def save(self, **kwargs):
        if self.content_type is None:
            # If content type guessing fails,
            # use octet stream as a major fallback
            self.content_type = "application/octet-stream"
        super(DBFile, self).save(**kwargs)
