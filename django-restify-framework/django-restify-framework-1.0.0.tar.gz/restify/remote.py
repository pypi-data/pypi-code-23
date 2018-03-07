from django.utils import six
from django.db.models.base import ModelBase
from django.db.models.options import DEFAULT_NAMES


class OverridableMeta(ModelBase):
    def __new__(mcls, name, bases, attrs):
        Meta = attrs.get("Meta", None)

        extra_attributes = {}
        if Meta:
            for attr in dir(Meta):
                if attr.startswith('__'):
                    continue

                if attr not in DEFAULT_NAMES:
                    extra_attributes[attr] = getattr(Meta, attr)
                    delattr(Meta, attr)

            attrs['Meta'] = Meta

        cls = super(OverridableMeta, mcls).__new__(mcls, name, bases, attrs)

        if Meta:
            for attr, value in extra_attributes.items():
                setattr(cls._meta, attr, value)

        return cls


class CustomMetaModel(six.with_metaclass(OverridableMeta)):
    pass


class RemoteModel(CustomMetaModel):
    class Meta:
        abstract = True
        api_entity_resource = None
        api_queryset_resource = None
