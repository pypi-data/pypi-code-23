


from rest_framework import serializers

from .models import GenericImage


class GenericImageSerializer(serializers.ModelSerializer):

    width = serializers.ReadOnlyField(source='image.width')
    height = serializers.ReadOnlyField(source='image.height')
    parsed_url = serializers.ReadOnlyField(source='image.parsed_url')

    class Meta:
        model = GenericImage
        fields = ('pk', 'image', 'width', 'height', 'parsed_url')