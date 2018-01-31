from flask_restful import Api, Resource, abort, reqparse
from marshmallow import Schema
from flask import request

from elask import mixins

class GenericAPIView(Resource):
    """
    Base class for all generic views
    """
    model = None
    name = None
    filter_fields = None
    action = None

    def get_current_index(self):
        return self.model._doc_type.index

    def get_current_doc_type(self):
        return self.model._doc_type.name

    @property
    def index(self):
        return self.get_current_index()

    @property
    def doc_type(self):
        return self.get_current_doc_type()

    def get_serializer_class(self):
        """
        To return the required serializer class
        """
        # Check parser is defined
        if hasattr(self, 'parser'):
            # Check parser is defined for the action
            if self.parser.get(self.action, None) is None:
                # Check if default parser is defined
                if self.parser.get('default', None) is None:
                    raise NotImplementedError
                else:
                    if issubclass(self.parser['default'], Schema) is False:
                        raise ValueError("Invalid Serializer Specified")
                    return self.parser['default']
            # Check is subclass of schema
            if issubclass(self.parser[self.action], Schema) is False:
                raise ValueError("Invalid Serializer Specified")
            return self.parser[self.action]
        # Check seializer is defined
        if hasattr(self, 'serializer') is False:
            raise NotImplementedError
        return self.serializer


class CreateAPIView(mixins.CreateModelMixin,
                    GenericAPIView):
    """
    Concrete view for creating a document instance.
    """
    def post(self, *args, **kwargs):
        """
        on method 'POST'
        """
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing documents.
    """
    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    """
    Concrete view for retrieving a document instance.
    """
    def get(self, *args, **kwargs):
        """
        on method 'GET' with pk
        """
        return self.retrieve(request, *args, **kwargs)


class ListRetrieveView(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin, GenericAPIView):
    """
    Concrete view for listing and retrieving document instance(s).
    """
    def get(self, *args, **kwargs):
        """
        on method 'GET' with pk
        """
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin,
                     GenericAPIView):
    """
    Concrete view for deleting a document instance.
    """
    def delete(self, *args, **kwargs):
        """
        on method 'DELETE'
        """
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin,
                    GenericAPIView):
    """
    Concrete view for updating a document instance.
    """
    def put(self, *args, **kwargs):
        """
        on method 'PUT'
        """
        return self.update(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        on method 'PATCH'
        """
        return self.update(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):
    """
    Concrete view for listing documents or creating a document instance.
    """
    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        return self.list(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        on method 'POST'
        """
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericAPIView):
    """
    Concrete view for retrieving, updating a document instance.
    """
    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        on method 'PUT'
        """
        return self.update(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        on method 'PATCH'
        """
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        return self.retrieve(request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        on method 'DELETE'
        """
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        method 'PUT'
        """
        return self.update(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        method 'PATCH'
        """
        return self.update(request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        method 'DELETE'
        """
        return self.destroy(request, *args, **kwargs)
