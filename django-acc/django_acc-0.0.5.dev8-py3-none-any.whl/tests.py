from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Organization, Profile

# Create your tests here.


class CreateUserTestCase(APITestCase):
    def setUp(self):
        url = reverse('create-user')
        resp = self.client.post(
            url,
            {'username': 'hehe', 'name': 'Mr. Hehe', 'password': 123},
            format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('password'), None,
                         'no password, even if hashed, should be returned')

    def test_associated_profile_and_organization(self):

        new_user = User.objects.get(username='hehe')
        new_profile = Profile.objects.get(user=new_user)
        self.assertEqual(new_profile.name, 'Mr. Hehe',
                'an associated profile with the new user should be also created')  # noqa

        implicit_default_organization = Organization.objects.get(slug='hehe')
        self.assertNotEqual(implicit_default_organization,
                            None,
                            "An organization named 'hehe' with default=True should be created implicitly")  # noqa

    def test_duplicated_user(self):
        url = reverse('create-user')
        resp = self.client.post(
            url, {'username': 'hehe', 'password': 123}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,
                         "Create an existing user should return 400")

    def test_login(self):
        url = reverse('login')
        resp = self.client.post(
            url, {'username': 'hehe', 'password': 123}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK,
                         "Newly created user should be logged in without error")  # noqa

        resp = self.client.post(
            url, {'username': 'hehe', 'password': 'wrongpass'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,
                         "Wrong password shoud return 400")

    def test_retrieve_user(self):
        retrieve_url = reverse('user-detail', kwargs={'pk': 1})
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.data['username'], 'hehe')

    def test_invalid_ser(self):
        url = reverse('create-user')
        resp = self.client.post(
            url, {'username': 'u1', 'password': ''}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', resp.data['password'])

    def tearDown(self):
        pass
