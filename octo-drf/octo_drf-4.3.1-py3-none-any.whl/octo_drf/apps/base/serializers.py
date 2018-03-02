import logging
from collections import OrderedDict
from rest_framework import serializers

logger = logging.getLogger('console_warnings')


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Базовая модель сериалайзера

    image_fields = [] определяет список полей SorlImageField, которые будут отдаваться в распарсеном виде
    """

    image_fields = []

    def get_fields(self):
        fields = super().get_fields()
        images = self._get_image_fields()
        fields.update(images)
        return fields

    def _get_image_fields(self):
        """
        Создает read_only поля по SorlImageField, вызывая метод parsed_url
        """
        fields = {}
        for field in self.image_fields:
            field_name = '{}_parsed'.format(field)
            fields[field_name] = serializers.ReadOnlyField(source='{}.parsed_url'.format(field))
        return fields

    def _filter_response(self, request, response):
        """
        Фильтрует поля сериалайзера по переданному гет параметру '_fields'
        _fields должен представлять собой строчку с полями разделенными запятой
        """
        fields = request.query_params.get('_fields')
        if fields:
            return OrderedDict(
                {field: response[field] for field in response if field in fields}
            )
        return response

    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if not request:
            logger.info(
                'Контекст не был передан в сериалазайер {}'.format(self.__class__.__name__)
            )
            return response
        return self._filter_response(request, response)
