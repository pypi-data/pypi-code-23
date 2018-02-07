


from rest_framework import serializers

from octo_drf.apps.base.serializers import BaseModelSerializer
from .models import FormMeta, FormFieldMeta


class FormFieldMetaSerializer(BaseModelSerializer):
    image_fields = ['image']

    class Meta:
        model = FormFieldMeta
        fields = FormFieldMeta.get_serializer_fields()


class FormMetaSerializer(BaseModelSerializer):
    image_fields = ['success_image']

    fields_meta = FormFieldMetaSerializer(many=True)

    class Meta:
        model = FormMeta
        fields = FormMeta.get_serializer_fields('fields_meta')


class DefaultModelFormSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отправки форм, работает с моделями форм, которые наследуются от AbstractBaseForm
    """

    def create(self, validated_data):
        obj = super().create(validated_data)
        validated_data['request'] = self.context['request']
        obj.send_form_mail(validated_data)
        return obj
