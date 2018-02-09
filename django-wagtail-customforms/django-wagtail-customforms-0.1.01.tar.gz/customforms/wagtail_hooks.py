from django.conf.urls import include, url
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks
from . import urls
# from wagtail.wagtailforms.models import get_forms_for_user

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
        url(r'^forms/', include(urls, app_name='customforms', namespace='customforms')),
    ]


class FormsMenuItem(MenuItem):
    def is_shown(self, request):
        return True


@hooks.register('register_admin_menu_item')
def register_forms_menu_item():
    return FormsMenuItem(
        _('Forms'), urlresolvers.reverse('customforms:index'),
        name='forms', classnames='icon icon-form', order=700
    )
