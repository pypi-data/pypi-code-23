


from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from test_app.models import CatalogItem, CatalogCategory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def catalog_fixtures():
    category = CatalogCategory(name='Test category')
    category.save()
    item = CatalogItem(name='Test', category=category)
    item.save()
    return item, category


@pytest.fixture()
def client():
    client = APIClient()
    return client


class TestCatalogModels:

    def test_save(self, catalog_fixtures):
        item, category = catalog_fixtures
        assert CatalogCategory.objects.count() == 1
        assert CatalogItem.objects.count() == 1
        assert item.category == category
