import datetime
import random

import pytz
from django.test import TestCase
from restify.serializers import BaseSerializer


class Structure(object):
    value1 = random.randint(1, 100)
    value2 = datetime.datetime.now()

    def flatten(self):
        retval = {
            'value1': self.value1,
            'value2': self.value2
        }

        return retval


class NoFlattenStructure(object):
    value1 = random.randint(1, 100)
    value2 = datetime.datetime.now()
    value3 = [Structure(), Structure()]

    def __str__(self):
        return "%s %s" % (self.value1, self.value2)


class BaseSerializerTest(TestCase):
    def setUp(self):
        self.serializer = BaseSerializer()

    def test_serialize_with_flatten(self):
        obj = Structure()
        simple = self.serializer.flatten(obj)

        self.assertSequenceEqual(simple, obj.flatten())

    def test_serialize_no_flatten(self):
        obj = NoFlattenStructure()
        simple = self.serializer.flatten(obj)

        self.assertSequenceEqual(simple, str(obj))

    def test_serialize_None(self):
        """None is flatten to None"""
        obj = {'test_value': None}
        simple = self.serializer.flatten(obj)

        self.assertSequenceEqual(simple, obj)

    def test_serialize_with_fields(self):
        obj = NoFlattenStructure()
        serializer = BaseSerializer(fields=['value1'])

        simple = serializer.flatten(obj)

        self.assertEqual(simple, {'value1': obj.value1})

    def test_serialize_with_fields_deep(self):
        obj = NoFlattenStructure()
        serializer = BaseSerializer(fields=['value1',
                                            ('value3', ('value1',)),
                                            'value2'])

        simple = {
            'value1': obj.value1,
            'value2': obj.value2.strftime('%Y-%m-%d %H:%M:%S%z'),
            'value3': [
                {
                    'value1': obj.value3[0].value1
                },
                {
                    'value1': obj.value3[1].value1
                }
            ]
        }

        self.assertEqual(simple, serializer.flatten(obj))

    def test_serialize_with_fields_and_flatten(self):
        obj = NoFlattenStructure()
        serializer = BaseSerializer(fields=['value1',
                                            'value3',
                                            'value2'])

        simple = {
            'value1': obj.value1,
            'value2': obj.value2.strftime('%Y-%m-%d %H:%M:%S%z'),
            'value3': [
                {
                    'value1': obj.value3[0].value1,
                    'value2': obj.value3[0].value2
                },
                {
                    'value1': obj.value3[1].value1,
                    'value2': obj.value3[0].value2
                }
            ]
        }

        self.assertEqual(simple, serializer.flatten(obj))

    def test_serialize_datetime(self):
        serializer = BaseSerializer(fields=['datetime', 'datetime2'])

        budapest = pytz.timezone('Europe/Amsterdam')
        obj = {
            'datetime': datetime.datetime.now(tz=budapest),
        }
        obj['datetime2'] = obj['datetime']
        obj['datetime2'] = obj['datetime2'].replace(tzinfo=None)

        self.assertIsInstance(serializer.flatten(obj)['datetime'], str)
        self.assertEquals(serializer.flatten(obj)['datetime'],
                          obj['datetime'].strftime('%Y-%m-%d %H:%M:%S%z'))
        self.assertEquals(serializer.flatten(obj)['datetime2'],
                          obj['datetime'].strftime('%Y-%m-%d %H:%M:%S'))

    def test_override_datetime_format(self):
        with self.settings(RESTIFY_DATETIME_FORMATTING='%Y-%m-%d'):
            serializer = BaseSerializer(fields=['datetime'])
            budapest = pytz.timezone('Europe/Amsterdam')
            obj = {
                'datetime': datetime.datetime.now(tz=budapest),
            }

            self.assertEquals(serializer.flatten(obj)['datetime'],
                              obj['datetime'].strftime('%Y-%m-%d'))
