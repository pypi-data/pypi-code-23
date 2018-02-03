from rest_framework import serializers
from django_framework.django_helpers.serializer_helpers import BaseSerializer

class ProfileMSBaseSerializer(BaseSerializer):
#     profile_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        
        model = None
        fields = BaseSerializer.Meta.fields + [
            'profile_pid',
        ]
        
        read_only_fields = ["id", "type", "last_updated", "created_at"]  # note that UUID is removed
        hidden_fields = BaseSerializer.Meta.hidden_fields # attempting to PUT to it will error.
        write_once_fields = BaseSerializer.Meta.write_once_fields # can only be set upon creation. not editable after
        
