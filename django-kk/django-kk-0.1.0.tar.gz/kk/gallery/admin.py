from django.contrib import admin
from django.db import models
from django import forms
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from sorl.thumbnail.fields import ImageField
from sorl.thumbnail import get_thumbnail


class ImageWidget(ClearableFileInput):
    template_name = 'admin/widgets/image.html'

#    def render(self, name, value, attrs = None, renderer = None):
##        get_thumbnail(obj.image, '150x150')
##        print(type(value));
##        print(attrs);
#        output = super(ImageWidget, self).render(name, value, attrs, renderer)
#        return output


class ImageListMixin(admin.ModelAdmin):

    def image_list_display(self, obj, **kwargs):
        return format_html('<img src="{url}" />'.format(
            url = get_thumbnail(obj.original_image, '150x150').url
        ))
    image_list_display.short_description = 'Изображение'


class GalleryAdminWidget(forms.FileInput):
#    template_with_initial = '%(clear_template)s<br />%(input_text)s: %(input)s'
#    template_with_clear = ('%(clear)s <label style="width:auto" for="%(clear_checkbox_id)s">'
#                           '%(clear_checkbox_label)s</label>')

    def render(self, name, value, attrs=None):
        output = super(SimpleGalleryAdminWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            try:
                thumb = get_thumbnail(value, '150')
            except Exception as e:
                pass
                logger.warn('Не удаётся получить миниатюры', exc_info=e)

            try:
                output = (
                    '<div class="grimo-thumbnail">'
                    '<a class="grimo-thumbnail__link" href="%s" target="_blank">'
                    '<img class="grimo-thumbnail__image" src="%s"></a>'
                    '<br />%s'
                    '</div>'
                ) % (value.url, thumb.url, output)
            except AttributeError:
                pass
        return mark_safe(output)


class GalleryBaseAdmin(admin.ModelAdmin):
    list_display = ('image_list_display', 'position', 'status')
    list_per_page = 80
#    ordering = ('-is_unordered', 'position', )

    fields = ('status', 'position', 'image',)

#    def get_queryset(self, request):
#        qs = super(GalleryBaseAdmin, self).get_queryset(request)
#        qs = qs.annotate(is_unordered = models.Count('position'))
#        return qs
#
#    def is_unordered(self, obj):
#        return obj.is_unordered
#    is_unordered.admin_order_field = 'is_unordered'


    def image_list_display(self, obj, **kwargs):
        return format_html('<img src="%s" />' % get_thumbnail(obj.image, '150x150').url)
    image_list_display.short_description = 'Изображение'

    def formfield_for_dbfield(self, obj, **kwargs):
        if isinstance(obj, ImageField):
            return obj.formfield(widget = GalleryAdminWidget)
        sup = super(GalleryBaseAdmin, self)
        return sup.formfield_for_dbfield(obj, **kwargs)

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs = {'rows': 4})},
    }


class SimpleGalleryAdmin(GalleryBaseAdmin):
    list_display = ('image_list_display', 'caption', 'position', 'status')
    fields = ('status', 'position', 'caption', 'image')

class SimpleBannerAdmin(GalleryBaseAdmin):
    list_display = ('image_list_display', 'text', 'position', 'status')
    fields = ('status', 'position', 'text', 'image')
