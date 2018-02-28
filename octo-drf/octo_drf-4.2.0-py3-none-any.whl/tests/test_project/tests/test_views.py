


from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from test_app.models import CatalogItem, CatalogCategory


pytestmark = pytest.mark.django_db


@pytest.fixture()
def client():
    client = APIClient()
    return client


class TestCatalogViews:

    def test_list_items(self, client):
        response = client.get(reverse('catalog_items-list'))
        assert response.status_code == 200

    def test_list_categories(self, client):
        response = client.get(reverse('catalog_categories-list'))
        assert response.status_code == 200
