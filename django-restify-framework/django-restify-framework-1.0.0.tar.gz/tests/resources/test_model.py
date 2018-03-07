from django import forms
from django.test import Client, override_settings

from restify.testing import LiveApiTestCase
from restify.resource import ModelResource, QuerysetResource
from restify.serializers import ModelSerializer

from tests.models import Person


class PersonResource(ModelResource):
    class Meta:
        model = Person
        resource_name = 'person'
        serializer = ModelSerializer(fields=("first_name", "last_name",
                                             ("instrument", ("name",))
                                            ))


class PersonSetResource(QuerysetResource):
    class Meta:
        queryset = Person.objects.filter(first_name__startswith='B')
        resource_name = 'persons'
        serializer = ModelSerializer(fields=("first_name", "last_name"))


class ModelResourceTest(LiveApiTestCase):
    RESOURCE = PersonResource

    def setUp(self):
        Person.objects.create_test_data()

    def test_get_form(self):
        resource = PersonResource()
        form = resource.get_form(data={'first_name': 'asdf'})

        self.assertIsInstance(form, forms.ModelForm)
        self.assertEqual(form.is_bound, True)
        self.assertEqual(form.is_valid(), False)

    def test_get_object(self):
        pers = Person.objects.first()
        response = self.get(pk=pers.pk)

        data = {
            "first_name": pers.first_name,
            "last_name": pers.last_name,
            "id": pers.pk,
            "instrument": {
                "id": pers.instrument.pk,
                "name": pers.instrument.name,
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, data)

    @override_settings(MIDDLEWARE=(
        'restify.middleware.PostInBodyMiddleware',
    ))
    def test_create_object(self):
        pers = Person.objects.first()
        count = Person.objects.count()
        data = {
            "first_name": "Test",
            "last_name": "Test",
            "age": 10,
            "instrument": pers.instrument.pk
        }

        response = self.post(pk='new', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.count(), count + 1)

    @override_settings(MIDDLEWARE=(
        'restify.middleware.PostInBodyMiddleware',
    ))
    def test_create_invalid(self):
        response = self.post(pk='new', data={'first_name': 'Test'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json.keys()), set(['age', 'last_name']))

    """def test_update_object(self):
        pers = Person.objects.first()

        response = self.put(pk=pers.pk, data={'first_name': 'Updated'})
        self.assertEqual(response.status_code, 200)
        #self.assertEquals()

        pers.refresh_from_db()
        self.assertEquals(pers.first_name, 'Updated')"""


class QuerysetResourceTest(LiveApiTestCase):
    RESOURCE = PersonSetResource

    def setUp(self):
        Person.objects.create_test_data()

    def test_get_persons(self):
        response = self.get()

        data = [{'first_name': _.first_name, 'last_name': _.last_name, 'id': _.pk}
                for _ in self.RESOURCE.Meta.queryset]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, data)
