from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import permissions

from .serializers import UserSerializer

class UserCreate(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [ permissions.AllowAny,]

@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def login(request):
    user = authenticate(username=request.data['username'], password=request.data['password'])
    if user is not None:
        # Get the token If None, create new token
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'message': 'username and password mismatched'}, status.HTTP_400_BAD_REQUEST)
