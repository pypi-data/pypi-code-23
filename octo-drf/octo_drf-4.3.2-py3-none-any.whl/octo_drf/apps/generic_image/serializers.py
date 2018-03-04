from rest_framework import serializers
from .models import GenericImage


class GenericImageSerializer(serializers.ModelSerializer):
    width = serializers.ReadOnlyField(source='image.width')
    height = serializers.ReadOnlyField(source='image.height')
    parsed_url = serializers.ReadOnlyField(source='image.parsed_url')

    class Meta:
        model = GenericImage
        fields = ('pk', 'image', 'width', 'height', 'parsed_url')


class GenericImageDetailSerializer(GenericImageSerializer):
    width = serializers.ReadOnlyField(source='image.width')
    height = serializers.ReadOnlyField(source='image.height')
    parsed_url = serializers.ReadOnlyField(source='image.parsed_url')

    class Meta:
        model = GenericImage
        fields = ('pk', 'image', 'width', 'height', 'parsed_url')

class GenericImageListSerializerMixin(serializers.Serializer):
    gallery_count = serializers.SerializerMethodField()

    def get_gallery_count(self, instance):
        return self.queryset.get(id=instance.id).count_gallery