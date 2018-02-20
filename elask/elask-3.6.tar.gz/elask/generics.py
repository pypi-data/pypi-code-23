from flask import request

from elask import mixins
from flask_jwt import current_identity, jwt_required
from flask_restful import Api, Resource, abort, reqparse
from marshmallow import Schema
from settings.dev import ENABLE_JWT, TENANT_FIELD


class GenericAPIView(Resource):
    """
    Base class for all generic views
    """
    model = None
    name = None
    filter_fields = None
    action = None
    tenant = False
    lookup_field = 'id'

    @property
    def index(self):
        return self.get_current_index()

    @property
    def doc_type(self):
        return self.get_current_doc_type()

    @property
    def _lookup_field(self):
        return getattr(self, 'lookup_field', 'id')

    def get_current_doc_type(self):
        return self.model._doc_type.name

    def get_current_index(self):
        if self.tenant is False:
            return self.model._doc_type.index
        if current_identity:
            return current_identity[TENANT_FIELD]
        else:
            pass # TODO: Need to handle

    def is_auth_required(self, action='default'):
        """
        To return the required action authentication 
        required configuration
        """
        if ENABLE_JWT is False:
            return False
        auth = getattr(self, 'Authentication', None)
        if auth is None:
            return False
        if isinstance(auth, bool):
            return auth
        if isinstance(auth, dict):
            return auth.get(action, False)
        return False

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
    
    def _post(self, request, *args, **kwargs):
        """
        on method 'POST'
        """
        return self.create(request, *args, **kwargs)

    @jwt_required()
    def _jpost(self, request, *args, **kwargs):
        return self._post(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        on method 'POST'
        """
        if self.is_auth_required('create'):
            return self._jpost(request, *args, **kwargs)
        return self._post(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing documents.
    """
    def _get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @jwt_required()
    def _jget(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self.is_auth_required('list'):
            return self._jget(request, *args, **kwargs)
        return self._get(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    """
    Concrete view for retrieving a document instance.
    """

    def _retrieve(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        return abort(404, message="Invalid Lookup")


class ListRetrieveView(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin, GenericAPIView):
    """
    Concrete view for listing and retrieving document instance(s).
    """
    def _get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def _retrieve(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @jwt_required()
    def _jget(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        else:
            if self.is_auth_required('list'):
                return self._jget(request, *args, **kwargs)
            return self._get(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin,
                     GenericAPIView):
    """
    Concrete view for deleting a document instance.
    """

    def _delete(self, request, *args, **kwargs):
        """
        method 'DELETE'
        """
        return self.destroy(request, *args, **kwargs)

    @jwt_required()
    def _jdelete(self, request, *args, **kwargs):
        return self._delete(request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        method 'DELETE'
        """
        if self.is_auth_required('delete') or self.is_auth_required('destroy'):
            return self._jdelete(request, *args, **kwargs)
        return self._delete(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin,
                    GenericAPIView):
    """
    Concrete view for updating a document instance.
    """

    def _put(self, request, *args, **kwargs):
        """
        method 'PUT'
        """
        return self.update(request, *args, **kwargs)

    @jwt_required()
    def _jput(self, request, *args, **kwargs):
        return self._put(request, *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        method 'PUT'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        method 'PATCH'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):
    """
    Concrete view for listing documents or creating a document instance.
    """

    def _get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def _post(self, request, *args, **kwargs):
        """
        on method 'POST'
        """
        return self.create(request, *args, **kwargs)

    @jwt_required()
    def _jget(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    @jwt_required()
    def _jpost(self, request, *args, **kwargs):
        return self._post(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self.is_auth_required('list'):
            return self._jget(request, *args, **kwargs)
        return self._get(request, *args, **kwargs)
    
    def post(self, *args, **kwargs):
        """
        on method 'POST'
        """
        if self.is_auth_required('create'):
            return self._jpost(request, *args, **kwargs)
        return self._post(request, *args, **kwargs)


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericAPIView):
    """
    Concrete view for retrieving, updating a document instance.
    """
    
    def _retrieve(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def _put(self, request, *args, **kwargs):
        """
        method 'PUT'
        """
        return self.update(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    @jwt_required()
    def _jput(self, request, *args, **kwargs):
        return self._put(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        return abort(404, message="Invalid Lookup Field")
    
    def put(self, *args, **kwargs):
        """
        method 'PUT'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        method 'PATCH'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    
    def _retrieve(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def _delete(self, request, *args, **kwargs):
        """
        method 'DELETE'
        """
        return self.destroy(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    @jwt_required()
    def _jdelete(self, request, *args, **kwargs):
        return self._delete(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        return abort(404, message="Invalid Lookup Field")

    def delete(self, *args, **kwargs):
        """
        method 'DELETE'
        """
        if self.is_auth_required('delete') or self.is_auth_required('destroy'):
            return self._jdelete(request, *args, **kwargs)
        return self._delete(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    
    def _retrieve(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def _put(self, request, *args, **kwargs):
        """
        method 'PUT'
        """
        return self.update(request, *args, **kwargs)

    def _delete(self, request, *args, **kwargs):
        """
        method 'DELETE'
        """
        return self.destroy(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    @jwt_required()
    def _jput(self, request, *args, **kwargs):
        return self._put(request, *args, **kwargs)

    @jwt_required()
    def _jdelete(self, request, *args, **kwargs):
        return self._delete(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        return abort(400, message="Invalid Lookup Field")
        
    def put(self, *args, **kwargs):
        """
        method 'PUT'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        method 'PATCH'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        method 'DELETE'
        """
        if self.is_auth_required('delete') or self.is_auth_required('destroy'):
            return self._jdelete(request, *args, **kwargs)
        return self._delete(request, *args, **kwargs)
