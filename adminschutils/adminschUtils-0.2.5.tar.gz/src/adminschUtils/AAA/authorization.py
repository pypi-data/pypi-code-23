"""
Authorization module
"""
import logging
from functools import wraps
from sanic.request import Request
from sanic import response

from ..config import Config
from ..connections.oauthclient import OAuthClient

__AUTHOR_LOGGER = logging.getLogger(__name__)


async def _oauth_authorization(request: Request, resource_server: str, required_value: str, client_name=None) -> bool:
    r"""
    AD authorization handler

    Args:
        request: HTTP request
        resource_server(str): Name of the resource server, it should be defined in config file.
        required_value(str): This value should be in the oAuth response
    Returns:
        Returns a bool based on the success of the authorization.

    """
    client_n = client_name or resource_server
    config = Config().get_service_conf()['connections']['oauthclient'][client_n]

    oauth_name = Config().get_service_conf()['token_provider']
    client = OAuthClient.get_instance(oauth_name)
    req = request.json
    token = req['token']
    data = await client.request_data(token)
    key = config['resource_server']['key']

    __AUTHOR_LOGGER.debug("OAuth authentication is used for request: %s, resource server: %s", str(request.body), resource_server)

    return data and required_value in data[key]


async def _true_authorization(request: Request, **kwargs) -> bool:  # pylint: disable=unused-argument
    r"""
    True authorization

    Args:
        request: HTTP request
        **kwargs:

    Returns:
        It returns True always
    """
    __AUTHOR_LOGGER.debug("True authorization is used for request %s", str(request))
    decision = True
    return decision


async def _false_authorization(request: Request, **kwargs) -> bool:  # pylint: disable=unused-argument
    r"""
    False authorization

    Args:
        request: HTTP request
        **kwargs:

    Returns:
        It returns False always
    """
    __AUTHOR_LOGGER.debug("False authorization is used for request %s", str(request))
    decision = False
    return decision


__authorization_services__ = {'oauth': _oauth_authorization,
                              'true': _true_authorization,
                              'false': _false_authorization
                             }
"""
Authorization method store. It's a dict where key is the name of the method value is the method handler function.
"""


def authorized(autorization_type: str, **arguments):
    r"""
    Decorator for authorizator function. Only named arguments are accepted

    Args:
        autorization_type (str): name of the handler method
        **arguments: these arguments passed to the handler

    Returns:
        Decorator for authorization
    """
    def _decorator(wrapped_function):
        """
        Authorization decorator
        Args:
            wrapped_function: Wrapped function

        Returns:
            Decorated function
        """
        @wraps(wrapped_function)
        async def _decorated_function(request, *original_args, **original_kwargs):
            is_authorized = await authorizator(request, autorization_type,**arguments)
            if is_authorized:
                __AUTHOR_LOGGER.debug("Successfully authorized.")
                return await wrapped_function(request, *original_args, **original_kwargs)
            else:
                __AUTHOR_LOGGER.info("Authorized failed.")
                return response.json({}, status=403)
        return _decorated_function
    return _decorator


async def authorizator(request: Request, autorization_type: str, **kwargs) -> bool:
    r"""
    Authorization function factory. Only named arguments are accepted.
    It calls the selected handler function and returns its decision.

    Args:
        request: HTTP request object
        autorization_type (str): name of the handler method
        **kwargs: these arguments passed to the handler

    Returns:
        bool based on the handler function
    """
    __AUTHOR_LOGGER.debug("Authorization request with params: %s", kwargs)
    handler = __authorization_services__[autorization_type]
    return await handler(request=request, **kwargs)
