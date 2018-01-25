from django.test import TestCase
from django.db import models
from .models import (Product, WarehouseEntry, ProductCategory, ExtremeWidget,
                        SaleInvoice, Employee, ProductRating, Property, PropertyOwner)


class DisablingTrackingTest(TestCase):


    def test_disable_enable_instance(self):
        ProductCategory.objects.create(name = 'test category', description = 'test')
        ProductCategory.objects.create(name = 'test category2', description = 'test')
        c1 = ProductCategory.objects.get(name = 'test category')
        c2 = ProductCategory.objects.get(name = 'test category2')
        self.assertTrue(c1.django_cdc.is_tracking_enabled())
        c1.django_cdc.disable_tracking()
        self.assertFalse(c1.django_cdc.is_tracking_enabled())
        self.assertTrue(c2.django_cdc.is_tracking_enabled())


    def test_disable_enable_class(self):
        self.assertRaises(ValueError, ProductCategory.django_cdc.disable_tracking)
        self.assertRaises(ValueError, ProductCategory.django_cdc.enable_tracking)
        self.assertRaises(ValueError, ProductCategory.django_cdc.is_tracking_enabled)

    def test_disabled_not_tracking(self):
        ProductCategory(name = 'test category', description = 'test').save()
        ProductCategory(name = 'test category2', description = 'test').save()
        c1 = ProductCategory.objects.get(name = 'test category')
        c2 = ProductCategory.objects.get(name = 'test category2')
        c1.description = 'best'
        c1.django_cdc.disable_tracking()
        c1.save()
        self.assertEquals(c1.django_cdc.all().count(), 1)
        c1.django_cdc.enable_tracking()
        c1.description = 'new desc'
        c1.save()
        self.assertEquals(c1.django_cdc.all().count(), 2)
        c1.django_cdc.disable_tracking()
        c1.delete()
        self.assertEquals(ProductCategory.django_cdc.all().count(), 3)
