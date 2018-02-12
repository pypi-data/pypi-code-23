
from django.db import models
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from flatpages.forms import FlatpageForm
from flatpages.models import FlatPage
from flatpages.lib import get_editor_widget
from flatpages.settings import DEFAULT_EDITOR


class FlatPageAdmin(TranslationAdmin):

    form = FlatpageForm

    list_display = ['url', 'title']

    list_filter = ['registration_required']

    search_fields = ['url', 'title']

    def __init__(self, *args, **kwargs):

        if DEFAULT_EDITOR:
            self.formfield_overrides = {
                models.TextField: {'widget': get_editor_widget(DEFAULT_EDITOR)}
            }

        super(FlatPageAdmin, self).__init__(*args, **kwargs)


admin.site.register(FlatPage, FlatPageAdmin)
