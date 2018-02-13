from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from djabberd import handlers

# Authentication and permission have been explicitly disabled because
# we *don't* want the default ones. The only way to control access to
# the API is using IP address validation.


class InsecureAPIView(APIView):

    authentication_classes = ()
    permission_classes = ()


class AuthView(InsecureAPIView):
    """Validate `username` and `password` using `user_authentication`
    handler.

    """
    def get(self, request, format=None):
        username = request.GET.get('username')
        password = request.GET.get('password')
        if not (username and password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # We have a `username` and `password` and we pass them to the handler
        result = handlers.user_authentication(username, password)

        if result is True:
            return Response()

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserView(InsecureAPIView):
    """Validate that the user with `username` exists using `user_exists`
    handler.

    """
    def get(self, request, format=None):
        username = request.GET.get('username')
        if not username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # We have a `username` and we pass them to the handler
        result = handlers.user_exists(username)

        if result is True:
            return Response()

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RosterView(InsecureAPIView):
    """Retrieves the user's roster for the user with the given `username`
    using `retrieve_user_roster` handler.

    """
    def get(self, request, format=None):
        username = request.GET.get('username')
        if not username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # We have a `username` and we pass it to the handler
        result = handlers.retrieve_user_roster(username)

        if result is not None:
            return Response(result)

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ArchiveView(InsecureAPIView):

    def get(self, request, format=None):
        """Retrieves the user's archive for the user with the given `username`
        using `archive_get` handler.

        """
        username = request.GET.get('username')
        if not username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # Get args from query string to pass the to the handler
        args = dict(list(request.GET.copy().items()))
        # We don't want `username` in args later
        args.pop('username')

        archive = handlers.archive_get(username, **args)

        return Response(archive)

    def post(self, request, format=None):
        """Stores the messages sent in the body

        """
        handlers.archive_store(request.data)

        return Response()
