"""DRF serializers."""
from rest_framework import serializers


class CreatedUpdatedSerializer(serializers.Serializer):
    created_dt = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    updated_dt = serializers.DateTimeField(read_only=True)
    updated_by = serializers.CharField(read_only=True)

    class Meta:
        fields = ('created_dt', 'created_by',
                  'updated_dt', 'updated_by', )
