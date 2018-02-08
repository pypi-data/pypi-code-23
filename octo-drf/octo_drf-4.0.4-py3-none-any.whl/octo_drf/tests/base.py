


from django.db.models.base import ModelBase


class AbstractBaseTest:
    model = None
    view_set = None

    def get_model(self):
        assert type(self.model) == ModelBase, 'В атрибуте класса model, должна быть модель'
        return self.model

    def get_view_set(self):
        assert 'ReadOnlyModelViewSet' or  'ModelViewSet' in [i.__name__ for i in self.view_set.mro()], \
            'view_set должен содержать объект ReadOnlyModelViewSet или ModelViewSet'
        return self.view_set

    def get_empty_fields(self):
        model = self.get_model()
        models_fields = model._meta.get_fields()
        fields = {k.name: None for k in models_fields if k.__class__.__name__ == 'SorlImageField'}
        return fields
