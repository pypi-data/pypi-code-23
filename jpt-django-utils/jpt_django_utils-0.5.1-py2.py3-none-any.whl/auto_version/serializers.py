"""Auto version serializers."""
from rest_framework import serializers


class AutoIntVersionSerializer(serializers.Serializer):
    version = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('version',)
