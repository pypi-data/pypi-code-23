"""Util views.

Reusable Django Rest Framework based views for resource based endpoints.

"""
__all__ = [
    'APIView',
    'ListModelView',
    'CreateListModelView',
    'ModelView',
]

from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView as _APIView, set_rollback
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException as _APIException

from .mixins import (ListModelMixin, RetrieveModelMixin, UpdateModelMixin,
                     DestroyModelMixin, CreateModelMixin)
from .exceptions import APIException


def exception_handler(exc, context):
    """Custom CaptureV2 API error handler."""
    response = None
    if isinstance(exc, APIException):
        response = exc.as_response()
    elif isinstance(exc, Http404):
        response = Response({
            "status_cd": "9999",
            "status_desc": "Not found."
        }, status=status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, PermissionDenied):
        response = Response({
            "status_cd": "9999",
            "status_desc": "Permission denied."
        }, status=status.HTTP_403_FORBIDDEN)
    elif isinstance(exc, _APIException):
        print(vars(exc))
        print((exc))
        response = Response({
            "status_cd": "9999",
            "status_desc": exc.detail,
        }, status=exc.status_code)

    if response:
        set_rollback()
    return response


class APIView(_APIView):
    """Generic APIView. Should be used for non resource based endpoints.

    Custom version of rest_framework's APIView. Introduces conveniences for
    working with Jewel's API response format.

    Attributes
    ----------
    success_code : str
        Success code of a successful response
    success_description : str
        Success description of a successful response

    """
    success_code = "0000"
    success_description = "SUCCESSFUL"
    success_http_code = status.HTTP_200_OK

    def get_exception_handler(self):
        return exception_handler

    def success(self, data=None, status_code=None, status_description=None, http_code=None):
        if data is None:
            data = {}
        if status_code is None:
            status_code = self.success_code
        if status_description is None:
            status_description = self.success_description
        if http_code is None:
            http_code = self.success_http_code

        success_context = {
            "status_cd": status_code,
            "status_desc": status_description
        }
        success_context.update(data)
        context = success_context
        return Response(context, status=http_code)

    def failure(self, status_code="9999", status_description="", http_code=400):
        return JsonResponse({
            "status_cd": status_code,
            "status_desc": status_description,
        }, status=http_code)


class _BaseResourceView(APIView, GenericAPIView):
    """Base API view, not intended to be used directly."""

    def get_serializer(self, *args, reading=False, **kwargs):
        serializer_class = self.get_serializer_class(reading)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self, reading):
        return self.serializer_class


class ListModelView(ListModelMixin, _BaseResourceView):
    """Model list API endpoint view.

    In order to make use of this class the following attributes must be specified
    in the inheriting class::

        serializer_class : rest_framework.serializers.Serializer
            The serializer used to serialize the instance.
        queryset : django.db.models.Queryset
            Queryset of instances too return.
        response_key : str
            Key to return data.

    """

    def get_context(self):
        """Context by GET handler.

        Provided for easier overriding.
        """
        return self.list(self.request)

    def get(self, request):
        """Handle get requests."""
        return self.success(self.get_context())


class CreateListModelView(CreateModelMixin, ListModelView):
    """Model list and create API endpoint view.

    Additional Required attributes (See ListModelView)::

        create_response_key : str
            Key to return created instance data.

    See ``ListModelView`` for usage
    """

    def post_context(self):
        """Context used by POST handler.

        Provided for easier overriding.
        """
        return self.create(self.request)

    def post(self, request):
        """Handle post request."""
        return self.success(self.post_context())


class ModelView(UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, _BaseResourceView):
    """Model get and edit API endpoint view.

    In order to make use of this class the following attributes must be specified
    in the inheriting class:

    serializer_class : rest_framework.serializers.Serializer
        The serializer used to serialize the instance.
    queryset : django.db.models.Queryset
        Queryset of instances too return.
    lookup_field : str
        The model field that should be used to for performing object lookup of
        individual model instances.
    lookup_kwarg : str, optional
        The URL keyword argument that should be used for object lookup. The URL
        conf should include a keyword argument corresponding to this value.
        If unset this defaults to using the same value as lookup_field.
    not_found_code : str
        Status Code returned when object is not found
    not_found_description : str
        Status description returned when object is not found
    error_code_filed_mapping : dict
        See utils.mixins.UpdateModelMixin

    """

    def get_context(self):
        """Context used by GET handler."""
        return self.retrieve(self.request)

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        return self.success(self.get_context())

    def post_context(self):
        """Context used by POST handler."""
        return self.update(self.request)

    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        return self.success(self.post_context())

    def validate_delete(self, request, *args, **kwargs):
        """Override to provide custom exception handling.

        Raise an APIException to return bad requests.

        NOTES
        -----
        Depracated!
        Look into handling with Serializer level validation instead.

        """
        pass

    def delete(self, request, *args, **kwargs):
        """Delete request handling."""
        self.validate_delete(request, *args, **kwargs)
        self.destroy(request)

        return self.success()
