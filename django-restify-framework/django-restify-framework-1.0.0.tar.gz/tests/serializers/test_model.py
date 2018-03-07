from django.db import models
from django.test import TestCase

from restify.serializers import ModelSerializer


class Related(models.Model):
    first = models.CharField(max_length=10, default='first')


class Model1(models.Model):
    a = models.CharField(max_length=100)
    b = models.PositiveIntegerField(default=10)
    c = models.ForeignKey(Related, related_name='relmodel', on_delete=models.CASCADE)
    d = models.ManyToManyField(Related, related_name='relmodelm2m')
    e = models.OneToOneField(Related, related_name='relone', on_delete=models.CASCADE)


class ModelSerializerTestCase(TestCase):
    def setUp(self):
        obj = Related()
        obj.save()

        obj2 = Related()
        obj2.save()

        m = Model1(a='example', c=obj, e=obj2)
        m.save()
        m.d.add(obj2)

    def test_model_serializer_without_relations(self):
        obj = Model1.objects.first()
        serializer = ModelSerializer(fields=['a', 'b'])
        flatten = serializer.flatten(obj)

        serialized = {
            'id': obj.pk,
            'a': obj.a,
            'b': obj.b
        }

        self.assertEqual(flatten, serialized)

    def test_model_serializer_with_relations_id(self):
        obj = Model1.objects.first()
        serializer = ModelSerializer(fields=['a', 'b', 'c', 'd', 'e'])
        flatten = serializer.flatten(obj)

        serialized = {
            'id': obj.pk,
            'a': obj.a,
            'b': obj.b,
            'c': {
                'id': obj.c.pk,
            },
            'd': [{'id': _.id} for _ in obj.d.all()],
            'e': {
                'id': obj.e.pk,
            }
        }

        self.assertEqual(flatten, serialized)

    def test_model_serializer_with_relations_full(self):
        obj = Model1.objects.first()
        serializer = ModelSerializer(fields=['a', 'b',
                                             ('c', ('id', 'first')),
                                             ('d', ('first',)),
                                             ('e', ('first',))])
        flatten = serializer.flatten(obj)

        serialized = {
            'id': obj.pk,
            'a': obj.a,
            'b': obj.b,
            'c': {
                'id': obj.c.pk,
                'first': obj.c.first
            },
            'd': [{'id': _.id, 'first': _.first} for _ in obj.d.all()],
            'e': {
                'id': obj.e.pk,
                'first': obj.e.first
            }
        }

        self.assertEqual(flatten, serialized)

    def test_queryset_serialization(self):
        objs = Model1.objects.all()
        serializer = ModelSerializer(fields=['a', 'b', 'c'])
        first = serializer.flatten(objs.first())

        flatten = serializer.flatten(objs)

        self.assertIsInstance(flatten, list)
        self.assertEqual(flatten[0], first)
