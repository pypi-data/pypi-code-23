"""
Django REST framework handles the following exceptions, and automatically generates error responses:
  - Subclasses of APIException raised inside REST framework,
  - Django's Http404 exception,
  - and Django's PermissionDenied exception.

More info: http://www.django-rest-framework.org/api-guide/exceptions/

We capture them here, and reformat responses to our desired style.
"""
import logging

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from django_on_chain import SETTINGS
from django_on_chain.exceptions import ServiceError

logger = logging.getLogger(__name__)


def reformat_error_handler(e, context):
    if isinstance(e, ServiceError):
        return Response({
            'type': e.type,
            'message': e.message,
        }, status=e.suggested_http_status or status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = exception_handler(e, context)  # Call default exception handler to get the standard error response

    if response is None:
        logger.exception('Uncaught exception', extra={
            'request': context['request'],
            'exception': e,
        })

    reformat_errors = getattr(context.get('view', object()), 'reformat_errors', SETTINGS['REFORMAT_ALL_ERRORS'])

    if not reformat_errors:
        return response

    if response is None:
        return Response({
            'type': 'server_error',
            'message': _('Unknown error; please try again later'),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        message = _('Invalid request')
        if isinstance(e, exceptions.ValidationError):
            message += ': {}'.format(e.detail)
        response.data = {
            'type': 'bad_request',
            'message': message,
        }
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        response.data = {
            'type': 'not_found',
            'message': _('Resource was not found'),
        }
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        response.data = {
            'type': 'unauthorized',
            'message': _('Request is not authorized'),
        }
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        response.data = {
            'type': 'access_forbidden',
            'message': _('You do not have permission to perform this action.'),
        }
    elif isinstance(e, exceptions.APIException):
        response.data = {
            'type': e.default_code,
            'message': force_text(e.default_detail),
        }

    return response
