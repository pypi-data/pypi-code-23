"""Util mixins.

These mixins are designed to work alongside rest_framework's GenericAPIView.

Notes
-----
GenericAPIView must ALWAYS be the last class when inheriting.

"""
__all__ = [
    'ListModelMixin',
    'CreateModelMixin',
    'RetrieveModelMixin',
    'UpdateModelMixin',
    'DestroyModelMixin',
]

from django.http import Http404

from .exceptions import APIBadRequestException, APINotFoundException


class _ResponseKeyMixin:
    """Response data will be nested in a key with this name.

    Attributes
    ----------
    response_key : str
        Key to nest response data under. Defaults to `data`
    """
    response_key = 'data'

    def get_response_key(self):
        assert self.response_key is not None, "response_key not set on {0}".format(self.__class__.__name__)
        return self.response_key


class _ResponseNotFoundMixin:
    """Adds an APIException handler to get_object.

    When get_object fails to find an instance, raises an APIException.

    Attributes
    ----------
    not_found_code : str
        The status code value given to the raised exception.
    not_found_description : str
        The status description given to the raised exception.

    """
    not_found_code = "0001"
    not_found_description = "Instance not found"

    def get_object(self):
        """Get the instance, raise APIException if not found."""
        try:
            return super().get_object()
        except Http404:
            raise APINotFoundException(self.not_found_code, self.not_found_description)


class CreateModelMixin:
    """Adds a `.create()` method"""
    create_response_key = 'data'
    error_code_field_mapping = {}

    def get_error_code(self, field_name):
        """Retrieve the error code of a field, based on the mapping set.

        Returns 9999 if the field isn't found in the mapping.

        Attributes
        ----------
        field_name : str
            Field name

        """
        return self.error_code_field_mapping.get(field_name, '9999')

    def create(self, request):
        """Create a new instance."""
        serializer = self.get_serializer(data=request.data, reading=False)
        if not serializer.is_valid():
            for field_name, errors in serializer.errors.items():
                error_code = self.get_error_code(field_name)
                error_message = "Invalid \"{0}\": {1}".format(field_name, errors[0])
                raise APIBadRequestException(error_code, error_message)
        obj = serializer.save()

        serializer = self.get_serializer(instance=obj, reading=True)
        ret = {
            self.create_response_key: serializer.data
        }
        return ret


class ListModelMixin(_ResponseKeyMixin):
    """Similar to ListModel Mixin but nests the result under a key.

    Attributes
    ----------
    response_key : str
        See `_ResponseKeyMixin`
    table_headers : list
        List of dictionaries.
        title will be the label shown on the front-end.
        (field)name is the key the value is stored in.

        Sample format::

            {
                "title": "Key", "name": "key",
                "title": "Value", "name": "value",
                "title": "Last Updated By", "name": "last_updated",
            }

    """
    response_key = None
    table_headers = None

    def get_data(self):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, reading=True)
        return serializer.data

    def list(self, request):
        """Return a dictionary with serialized objects under a specified key.

        Parameters
        ----------
        request : Django Request
            Used to handle filtering.

        Returns
        -------
        dict
            The serialized data is nested within a key.

        Notes
        -----
        Filtering is not yet handled.

        """
        ret = {
            self.get_response_key(): self.get_data()
        }
        return ret


class RetrieveModelMixin(_ResponseKeyMixin, _ResponseNotFoundMixin):
    """Adds a `.retrieve()` method.

    Returns the instance's serialized data nested under the specified key.

    Attributes
    ----------
    not_found_code : str
        See `_ResponseNotFoundMixin`
    not_found_description : str
        See `_ResponseNotFoundMixin`

    """
    not_found_code = "0001"
    not_found_description = "Instance not found."

    def retrieve(self, request):
        """Return the object serialized as a dictionary."""
        instance = self.get_object()

        serializer = self.get_serializer(instance, reading=True)

        ret = {
            self.get_response_key(): serializer.data
        }
        return ret


class UpdateModelMixin(_ResponseKeyMixin, _ResponseNotFoundMixin):
    """Adds an `.update()` method.

    Attributes
    ----------
    error_code_field_mapping : dict
        A mapping of field names and error codes.
        The keys should be a string of a fieldname.
        Values should be the error code as a string.

    """
    error_code_field_mapping = {}

    def get_error_code(self, field_name):
        """Retrieve the error code of a field, based on the mapping set.

        Returns 9999 if the field isn't found in the mapping.

        Attributes
        ----------
        field_name : str
            Field name

        """
        return self.error_code_field_mapping.get(field_name, '9999')

    def update(self, request):
        """Update the instance from request data and return the new serialized instance.

        If validation fails, responds with the first error in the list.
        """
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, reading=False)
        if not serializer.is_valid():
            for field_name, errors in serializer.errors.items():
                error_code = self.get_error_code(field_name)
                error_message = "Invalid \"{0}\": {1}".format(field_name, errors[0])
                raise APIBadRequestException(error_code, error_message)
        obj = serializer.save()

        serializer = self.get_serializer(instance=obj, reading=True)
        ret = {
            self.get_response_key(): serializer.data
        }
        return ret


class DestroyModelMixin(_ResponseNotFoundMixin):
    """Adds a `.destroy()` method for deleting instances."""

    def destroy(self, request):
        """Delete the found instance."""
        instance = self.get_object()
        instance.delete()
