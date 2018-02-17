from . import models
from django.contrib import admin
from django.conf import settings

PAGE_SITE = getattr(settings, 'PAGE_SITE', 'page.Site')
PAGE_PAGE = getattr(settings, 'PAGE_PAGE', 'page.Page')
PAGE_USER = getattr(settings, 'PAGE_USER', 'page.Page_User')


if PAGE_PAGE == 'page.Page':
    admin.site.register(models.Page)
admin.site.register(models.Page_Version)

admin.site.register(models.File)
admin.site.register(models.UUID_File)

if PAGE_SITE == 'page.Site':
    admin.site.register(models.Site)
admin.site.register(models.Page_Editor)
#test