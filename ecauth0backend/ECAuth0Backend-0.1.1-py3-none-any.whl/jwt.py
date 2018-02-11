from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import ugettext
from ECAuth0Backend import settings
import jwt
from jwt.exceptions import InvalidTokenError
from ECAuth0Backend import backend
from ECAuth0Backend.settings import AUTH0_JWT_SECRET, AUTH0_JWT_CLIENT_ID


def _get_token_from_header(request):
    """
    Get the token from request headers.
    :param request: django request object
    :return: the token
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return
    separator = "{separator} ".format(separator=settings.AUTH0_JWT_HEADER_SEPARATOR)
    split = auth_header.split(separator)
    if len(split) != 2:
        raise exceptions.AuthenticationFailed(ugettext('Invalid auth header.'))
    return split[1]


def _parse_token(token):
    """
    Parse the given token.
    :param token: the JWT
    :return: decoded token dict
    """
    secret = AUTH0_JWT_SECRET
    audience = AUTH0_JWT_CLIENT_ID
    try:
        return jwt.decode(token, secret, audience=audience)
    except InvalidTokenError:
        raise exceptions.AuthenticationFailed(ugettext("Invalid Token."))


class Auth0JWTAuthentication(authentication.BaseAuthentication):
    """
    Allows user to be authenticated in te Django Rest Framework with a JWT from Auth0.
    For example you might override the authentication_classes of a DRF ViewSet as follows:
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
        Auth0JWTAuthentication,
    )
    """
    def authenticate(self, request):
        token = _get_token_from_header(request)
        if not token:
            return
        data = _parse_token(token)
        user = backend.get_or_create_user(
            user_id=data.get('sub'),
            email=data.get('email'),
            email_verified=data.get('email_verified', False),
            name=data.get('name'),
        )
        return user, None
