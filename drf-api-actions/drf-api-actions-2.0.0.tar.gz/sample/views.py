import coreapi
import coreschema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from drf_api_actions.views import ActionReadMixin


class UsersAPIView(APIView):
    """
    获得用户列表

    返回值：用户列表 `['a', 'b', ...]`

    """

    def get(self, request):
        return Response(['a', 'b'])


class InvitationAPIView(APIView):
    """
    获得用户列表

    返回值：用户列表 `['a', 'b', ...]`

    """

    def get(self, request):
        return Response(['i', 'j'])


class UsersActionReadAPIView(ActionReadMixin, APIView):
    """
    获得用户列表, 用了`ActionReadMixin`后这是一个用 Read

    返回值：用户列表 `['a', 'b', ...]`

    """

    def get(self, request):
        return Response(['a', 'b'])


class UsersExtraFieldsAPIView(APIView):
    """
    获得用户列表, 带user_id/user_name会过滤

    返回值：
        - 带user_id: `['a']`
        - 不带user_id: `['a','b']`
    """
    permission_classes = [permissions.IsAuthenticated,]

    schema = AutoSchema(manual_fields=[
        coreapi.Field(name='user_father', location='query', required=True,
                      schema=coreschema.String(description='用户的爹')),
        coreapi.Field(name='user_id', location='query', required=False,
                      schema=coreschema.Integer(description='用户id')),
        coreapi.Field(name='obj', location='query', required=False,
                      schema=coreschema.Object(description='object param')),
        coreapi.Field(name='arr', location='query', required=False,
                      schema=coreschema.Array(description='array param')),
        coreapi.Field(name='boo', location='query', required=False,
                      schema=coreschema.Boolean(description='boolean param')),
        coreapi.Field(name='enu', location='query', required=False,
                      schema=coreschema.Enum([1, 2, 3], description='enum param')),
    ])

    def get(self, request):
        user_id = request.GET.get('user_id', '')
        if user_id:
            return Response(['a'])
        else:
            return Response(['a', 'b'])
