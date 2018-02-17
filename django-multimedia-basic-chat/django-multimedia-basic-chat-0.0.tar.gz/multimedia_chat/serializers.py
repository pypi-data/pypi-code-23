from django.contrib.auth.models import User

# from commons.non_null_serializer import BaseSerializer
from multimedia_chat.models import (
    Message,
)
# from commons.attachments.models import AssetsManagement
from rest_framework import serializers


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'from_user_read',)


class MessageViewSerializer(serializers.ModelSerializer):
    sender = UserDetailSerializer()
    receiver = UserDetailSerializer()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'from_user_read')
