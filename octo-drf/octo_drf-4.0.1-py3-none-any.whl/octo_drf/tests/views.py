


from mixer.backend.django import mixer
from rest_framework.test import APIRequestFactory

from .base import AbstractBaseTest


class AbstractViewSetTest(AbstractBaseTest):

    lookup_field = 'slug'

    def _get_lookup_field(self, obj):
        return {self.lookup_field: getattr(obj, self.lookup_field)}

    def test_list(self):
        view_set = self.get_view_set()
        request = APIRequestFactory().get('')
        list_view = view_set.as_view({'get': 'list'})
        response = list_view(request)
        assert response.status_code == 200, 'Должен возвращаться 200'

    def test_retrieve(self):
        view_set = self.get_view_set()
        obj = mixer.blend(self.get_model(), **self.get_empty_fields())
        request = APIRequestFactory().get('')
        retrieve = view_set.as_view({'get': 'retrieve'})
        response = retrieve(request, **self._get_lookup_field(obj))
        assert response.status_code == 200, 'Должен возвращаться 200'
