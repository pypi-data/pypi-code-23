"""
Authentication module
"""
import logging
from functools import wraps
from sanic.request import Request
from sanic import response

__AUTH_LOGGER = logging.getLogger(__name__)


async def _true_authentication(request: Request, **kwargs) -> bool:  # pylint: disable=unused-argument
    r"""
    True authenticator

    Args:
        request: HTTP request
        **kwargs:

    Returns:
        It returns True always
    """
    __AUTH_LOGGER.debug("True authentication is used for request %s", str(request))
    decision = True
    return decision


async def _false_authentication(request: Request, **kwargs) -> bool:  # pylint: disable=unused-argument
    r"""
    False authenticator

    Args:
        request: HTTP request
        **kwargs:

    Returns:
        It returns False always
    """
    __AUTH_LOGGER.debug("False authentication is used for request %s", str(request))
    decision = False
    return decision

__authentication_services__ = {'true': _true_authentication,
                               'false': _false_authentication
                              }
"""
Authentication method store. It's a dict where key is the name of the method value is the method handler function.
"""


def authenticated(authentication_type: str, **arguments):
    r"""
    Decorator for authenticator function. Only named arguments are accepted.

    Args:
        request: HTTP request
        authentication_type (str): name of the handler method.
        **arguments: these arguments passed to the handler.

    Returns:

    """
    def _decorator(wrapped_function):
        """
        Authenticated decorator.
        Args:
            wrapped_function: Wrapped function

        Returns:

        """
        @wraps(wrapped_function)
        async def _decorated_function(request: Request, *args, **kwargs):
            is_authenticated = await authenticator(request, authentication_type, **arguments)
            if is_authenticated:
                __AUTH_LOGGER.debug("Successfully authenticated.")
                return await wrapped_function(request, *args, **kwargs)
            else:
                __AUTH_LOGGER.info("Failed authentication.")
                return response.json({}, status=403)
        return _decorated_function
    return _decorator


async def authenticator(request: Request, autorization_type: str, **kwargs) -> bool:
    r"""
    Authentication function factory. Only named arguments are accepted.
    It calls the selected handler function and returns its decision.

    Args:
        request: HTTP request object
        autorization_type: name of the handler method
        **kwargs: these arguments passed to the handler

    Returns:
        bool based on the handler function
    """
    __AUTH_LOGGER.debug("Authentication request with params: %s", kwargs)
    handler = __authentication_services__[autorization_type]
    return await handler(request=request, **kwargs)
