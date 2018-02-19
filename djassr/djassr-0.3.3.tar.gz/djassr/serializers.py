from rest_framework import serializers


class BaseNoModelSerializer(serializers.Serializer):
    def save(self):
        """We want the machinery from `CreateModelMixing` but no model exist.

        """
        pass


class PUTSignatureSerializer(BaseNoModelSerializer):

    file_name = serializers.CharField(required=False)
    mime_type = serializers.CharField()


class GETSignatureSerializer(BaseNoModelSerializer):

    object_name = serializers.CharField()
