"""
ViewSets are essentially just a type of class based view, that doesn't provide
any method handlers, such as `get()`, `post()`, etc... but instead has actions,
such as `list()`, `retrieve()`, `create()`, etc...
"""
from elask import mixins
from elask import generics

class ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   generics.ListRetrieveView,
                   generics.CreateAPIView,
                   generics.UpdateAPIView,
                   generics.DestroyAPIView):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `destroy()` and `list()` actions.
    """
    pass