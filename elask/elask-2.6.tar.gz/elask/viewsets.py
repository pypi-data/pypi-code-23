"""
ViewSets are essentially just a type of class based view, that doesn't provide
any method handlers, such as `get()`, `post()`, etc... but instead has actions,
such as `list()`, `retrieve()`, `create()`, etc...
"""
from flask import request

from elask import mixins
from elask import generics

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
    def get(self, *args, **kwargs):
        """
        method 'GET'
        """
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
    
    def post(self, *args, **kwargs):
        """
        on method 'POST'
        """
        return self.create(request, *args, **kwargs)

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
