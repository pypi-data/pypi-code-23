from django.conf.urls import url
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.views import APIView
from jwt_auth.views import obtain_jwt_token, refresh_jwt_token, register_user

try:
    from rest_framework_oauth.authentication import OAuth2Authentication
except ImportError:
    try:
        from rest_framework.authentication import OAuth2Authentication
    except ImportError:
        OAuth2Authentication = None



class MockView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return HttpResponse('mockview-get')

    def post(self, request):
        return HttpResponse('mockview-post')


urlpatterns = [
    url(r'^api-auth/', obtain_jwt_token),
    url(r'^auth-token-refresh/$', refresh_jwt_token),
    url(r'^api-register/', register_user),
]
