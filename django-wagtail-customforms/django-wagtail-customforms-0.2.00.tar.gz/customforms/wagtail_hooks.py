from django.conf.urls import include, url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks
from . import urls

from .models import Form


class FormAdmin(ModelAdmin):
    model = Form
    menu_label = 'Forms'
    menu_icon = 'date'
    panels = [
        InlinePanel('form_fields', label="Form fields"),
    ]

class MyModelAdminGroup(ModelAdminGroup):
    menu_label = 'My App'
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (FormAdmin,)
modeladmin_register(MyModelAdminGroup)


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^forms/', include(urls, namespace='customforms')),
    ]


class FormsMenuItem(MenuItem):
    def is_shown(self, request):
        return True


@hooks.register('register_admin_menu_item')
def register_forms_menu_item():
    return FormsMenuItem(
        _('Forms'), reverse('customforms:index'),
        name='forms', classnames='icon icon-form', order=700
    )
