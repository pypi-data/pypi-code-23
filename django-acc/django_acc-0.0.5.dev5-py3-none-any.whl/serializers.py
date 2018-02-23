from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer, HyperlinkedIdentityField
from rest_framework import status

class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        write_only_fields = ('password',)

    def create(self, validated_data):
        user = User.objects.create_user(
                validated_data['username'], 
                validated_data.get('email', None),
                validated_data['password'])
        return user




