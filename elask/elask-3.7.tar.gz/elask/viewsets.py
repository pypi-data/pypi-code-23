"""
ViewSets are essentially just a type of class based view, that doesn't provide
any method handlers, such as `get()`, `post()`, etc... but instead has actions,
such as `list()`, `retrieve()`, `create()`, etc...
"""
from flask import request
from flask_jwt import jwt_required
from flask_jwt import current_identity

from elask import mixins
from elask import generics

from settings.dev import ENABLE_JWT, TENANT_FIELD

class ModelViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,    
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `destroy()` and `list()` actions.
    """
    
    def _get(self, request, *args, **kwargs):
        """
        on method 'GET'
        """
        if self._parent_lookup_field in kwargs:
            return self.list_with_parent(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
    
    def _retrieve(self, request, *args, **kwargs):
        """
        on method 'GET' with lookup
        """
        if self._parent_lookup_field in kwargs:
            return self.retrieve_with_parent(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)
    
    def _post(self, request, *args, **kwargs):
        """
        on method 'POST'
        """
        if self._parent_lookup_field in kwargs:
            return self.create_with_parent(request, *args, **kwargs)
        return self.create(request, *args, **kwargs)

    def _put(self, request, *args, **kwargs):
        """
        method 'PUT'
        """
        if self._parent_lookup_field in kwargs:
            return self.update_with_parent(request, *args, **kwargs)
        return self.update(request, *args, **kwargs)

    def _delete(self, request, *args, **kwargs):
        """
        method 'DELETE'
        """
        if self._parent_lookup_field in kwargs:
            return self.destroy_with_parent(request, *args, **kwargs)
        return self.destroy(request, *args, **kwargs)

    @jwt_required()
    def _jget(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    @jwt_required()
    def _jpost(self, request, *args, **kwargs):
        return self._post(request, *args, **kwargs)

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
        else:
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
