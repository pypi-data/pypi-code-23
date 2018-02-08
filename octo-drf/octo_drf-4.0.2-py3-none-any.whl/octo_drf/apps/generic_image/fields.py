from functools import partial

from django.core import checks
from django.urls import NoReverseMatch
from django.urls import reverse
from django.db.models.fields.files import ImageFieldFile
from sorl.thumbnail import ImageField

from ..utils.helpers import parse_filename_to_args
from .storage import ImageStorage
from .path import image_upload_path


class ExtendedImageField(ImageFieldFile):
    #TODO: Комментарии
    def parsed_url(self, *args, **kwargs):
        try:
            prefix, _ = self.url.rsplit('/', 1)
        except ValueError:
            return None
        name, ext = _.split('.')
        return {'prefix': prefix + '/',
                'name': name,
                'ext': '.' + ext}


class SorlImageField(ImageField):
    #TODO: Комментарии
    def __init__(self, verbose_name=None, name=None, width_field=None,
                 height_field=None, lookup_name=None, **kwargs):
        self.lookup_name = lookup_name
        kwargs['storage'] = ImageStorage()
        kwargs['upload_to'] = partial(image_upload_path, lookup_name)
        super().__init__(verbose_name, name,
                                             width_field, height_field, **kwargs)

    def pre_save(self, model_instance, add):
        f = super().pre_save(model_instance, add)
        if f:
            try:
                reverse('image_storage', args=parse_filename_to_args(f.name))
            except NoReverseMatch:
                raise NoReverseMatch('Неправильный формат изображения, '
                                     'название и расширение файла не должно содержать специальных символов')
        return f

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['upload_to']
        return name, path, args, kwargs

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        if self.lookup_name != self.name:
            error = [
                checks.Error(
                    'SorlImageField lookup_name must be equal to '
                    'field name, now it is: "{}"'.format(self.lookup_name),
                    hint='Add lookup_name in SorlImageField',
                    obj=self,
                    id='fields.E210',
                )]
            errors.extend(error)
        return errors

    attr_class = ExtendedImageField
