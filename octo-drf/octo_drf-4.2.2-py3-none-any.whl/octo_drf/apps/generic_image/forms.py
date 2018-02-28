# -*- coding: utf-8 -*-

from django import forms
from sorl.thumbnail.fields import ImageFormField
from .models import GenericImage

class MultiFileInput(forms.FileInput):
    #TODO: Комментарии
    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]


class MultiplyImageUploadField(ImageFormField):
    #TODO: Комментарии
    widget = MultiFileInput

    def __init__(self, *args, **kwargs):
        self.max_files = kwargs.get('max_files', 25)
        super().__init__(*args, **kwargs)

    def to_python(self, data):
        images = []
        for item in data:
            image = super().to_python(item)
            if image:
                images.append(image)
        return images

    def validate(self, value):
        if len(value) > self.max_files:
            raise forms.ValidationError('Колличество загружаемых файлов должны быть меньше {}'.format(self.max_files))
        return super().validate(value)


class MultiplyImageFormMixin(forms.ModelForm):

    multiple_upload = MultiplyImageUploadField(
        label='Загрузка нескольких изображений',
        required=False
    )

    def save(self, commit=True):
        images = []
        if self.cleaned_data['multiple_upload']:
            for image in self.cleaned_data['multiple_upload']:
                if self.instance.id is None:
                    self.instance.save()
                # images.append(GenericImage(image=image, content_object=self.instance))
                GenericImage.objects.create(image=image, content_object=self.instance)
            # GenericImage.objects.bulk_create(images)
        return super().save(commit)
