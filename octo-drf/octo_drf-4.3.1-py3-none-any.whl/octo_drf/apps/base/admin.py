from itertools import chain

from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """
    Базовая модель для админки. Автоматически строит поля сортирует по филдсетам
    Расширяется с помощью списка филдсетов в extended_fieldsets.
    extended_fieldsets = [
        ('Мой филдсет', {
                'fields': ['text', 'title'],
                'order': 10
                })
    ]
    Филдсет может содержать необязательный ключ "order" для определения порядка вывода
    """
    extended_fieldsets = []

    def get_fieldsets(self, request, obj=None):
        """
        Создает дефолтный филдсет по полям модели.
        Расширяется с помощью extended_fieldsets
        """
        if self.fieldsets:
            return self.fieldsets
        fields = self._group_allowed_fields()
        fieldsets = [
            (None, {
                'fields': fields['general'],
                'order': 0
            }),
            ('Настройки', {
                'fields': fields['config'],
                'order': 9
            })]
        if self._check_for_image_mixin():
            fieldsets.append(('Мультизагрузка изображений', {
                                'fields': ['multiple_upload'],
                                'order': 10
                             }))
        self._extend_fieldsets(fieldsets)
        self._sort_fieldsets(fieldsets)
        self._remove_empty_values(fieldsets)
        return tuple(fieldsets)

    def _remove_empty_values(self, fieldsets):
        """
        Удаляет филдсеты с пустыми значениями
        """
        for index, field in enumerate(fieldsets):
            if not field[1]['fields']:
                fieldsets.pop(index)
        return fieldsets

    def _sort_fieldsets(self, fieldsets):
        """
        Сортирует по полю ордер и удаляет его, чтобы Django не ругался
        """
        fieldsets.sort(key=lambda x: x[1].get('order', 10))
        for field in fieldsets:
            field[1].pop('order', None)
        return fieldsets

    def _extend_fieldsets(self, fieldsets):
        """
        Расширяет дефолтный филдсет, используя extended_fieldsets
        """
        if not self.extended_fieldsets:
            return fieldsets
        self._remove_duplicate_fields(fieldsets)
        fieldsets.extend(self.extended_fieldsets)
        return fieldsets

    def _remove_duplicate_fields(self, fieldsets):
        """
        Удаляет поля из филдсета, если такие же есть в extended_fieldsets
        """
        ext_fields = (i[1]['fields'] for i in self.extended_fieldsets)
        flat_ext_fields = list(chain.from_iterable(ext_fields))
        for field in fieldsets:
            fields = field[1]['fields']
            [fields.remove(i) for i in fields if i in flat_ext_fields]
        return fieldsets

    def _group_allowed_fields(self):
        """
        Группирует поля из модели в категории "config" и "general
        """
        field_dict = dict()
        fields = self.model.get_admin_fields()
        fields.remove('id')
        field_dict['config'] = [i for i in fields if i in ['order', 'is_published']]
        field_dict['general'] = [i for i in fields if i not in ['order', 'is_published']]
        return field_dict

    def _check_for_image_mixin(self):
        """
        Проверяет, наличие MultiplyImageFormMixin в форме класса
        и наличие GalleryStackedInline в инлайнах.
        Нужно для подключения мультизагрузки изображений в форме
        """
        f = self.form
        inline_names = []
        form_mro = [i.__name__ for i in f.mro()]
        if self.inlines:
            inline_names = [i.__name__ for i in self.inlines]
        return 'MultiplyImageFormMixin' in form_mro and 'GalleryStackedInline' in inline_names


class CatalogAdmin(BaseAdmin):
    """
    Дефолтный класс с полями моделей каталога
    """
    list_display = ('name', 'slug', 'order', 'is_published')
    list_filter = ('is_published',)
    list_editable = ('is_published', 'order',)
    prepopulated_fields = {'slug': ('name',)}