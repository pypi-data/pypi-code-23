# -*- coding: utf-8 -*-
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from sorl.thumbnail.admin import AdminImageMixin
from .models import GenericImage

class GalleryStackedInline(AdminImageMixin, GenericStackedInline):

    model = GenericImage
    extra = 0
    fields = ('title', 'image', 'order', 'is_published')


class GalleryGenericTabularInline(AdminImageMixin, GenericTabularInline):
    model = GenericImage
    extra = 0
    fields = ('title', 'image', 'order', 'is_published')