from django.contrib.auth.models import User
from .models import Organization, Profile
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework import status


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'url')
        write_only_fields = ('password',)

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            # Allow request with no email address
            validated_data.get('email', None),
            validated_data['password'])
        return user


class ProfileSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class OrganizationSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ('name', 'owner', 'default', 'slug')
