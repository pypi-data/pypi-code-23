from django.core.paginator import Paginator
from django.test import TestCase

from restify.serializers import ModelSerializer, DjangoSerializer


class DjangoSerializerTest(TestCase):
    def setUp(self):
        self.serializer = DjangoSerializer()
        objects = ['john', 'paul', 'george', 'ringo']
        p = Paginator(objects, 2)
        self.page = p.page(2)

    def test_paginator_serializer(self):
        serialized = {
            "current": self.page.number,
            "list": [{'key': 1, 'value': 1}, {'key': 2, 'value': 2}, None], # previous, current, next (if we have)
            "num_pages": self.page.paginator.num_pages
        }

        simple = self.serializer.flatten(self.page)

        self.assertEqual(simple, serialized)