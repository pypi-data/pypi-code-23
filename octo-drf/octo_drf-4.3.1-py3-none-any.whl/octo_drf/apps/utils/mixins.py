from django.core.exceptions import ValidationError


class ModelURLSaveMixin:

    def save(self, *args, **kwargs):
        if not self.url.startswith('/'):
            self.url = '/' + self.url
        if not self.url.endswith('/'):
            self.url = self.url + '/'
        super().save(*args, **kwargs)


class SingletonMixin:

    validation_error = 'Может быть только один объект'

    def save(self, *args, **kwargs):
        model = self._meta.model
        if model.objects.count() == 1 and not self.pk:
            raise ValidationError(self.validation_error)
        super().save(*args, **kwargs)