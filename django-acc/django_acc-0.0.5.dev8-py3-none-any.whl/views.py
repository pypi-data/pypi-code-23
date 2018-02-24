from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import permissions

from .serializers import (UserSerializer,
                          OrganizationSerializer,
                          ProfileSerializer)


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Create the associated profile for user
        profile_serializer = ProfileSerializer(data={
            'user': serializer.data['url'],
            'name': request.data['name']
        })
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        # Create an implicit, default organization for the newly created user
        # WHY?
        # Every user has a implicit, default organization with the same name
        organization_serializer = OrganizationSerializer(data={
            'name': request.data['name'],
            'slug': request.data['username'],
            'default': True,
            'owner': serializer.data['url']
        })
        organization_serializer.is_valid(raise_exception=True)
        organization_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'username': serializer.data['username'],
                'email': serializer.data.get('email')
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class RetrieveUserView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny, ]


@api_view(['POST'])
@permission_classes([permissions.AllowAny, ])
def login(request):
    user = authenticate(
        username=request.data['username'], password=request.data['password'])
    if user is not None:
        # Get the token If None, create new token
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        return Response({'token': token.key})
    else:
        return Response(
            {'errors': ['username and password mismatched']},
            status.HTTP_400_BAD_REQUEST)
