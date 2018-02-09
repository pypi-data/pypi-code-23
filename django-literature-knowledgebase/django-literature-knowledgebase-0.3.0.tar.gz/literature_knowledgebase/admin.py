# -*- coding: utf-8
from django.contrib import admin

from . import models


class ArticleAdmin(admin.ModelAdmin):
    model = models.Article
    list_display = ('source', 'identifier', 'user', 'active', 'created', 'modified')
    raw_id_fields = ('user', )
    search_fields = ('user__username', 'identifier', 'description')
    list_filter = ('active', 'source', )
    save_as = True


admin.site.register(models.Article, ArticleAdmin)
