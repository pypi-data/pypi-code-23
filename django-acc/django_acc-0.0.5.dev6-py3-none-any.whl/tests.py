from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import Organization

# Create your tests here.
class IntegrationTest(APITestCase):
    def setUp(self):
        pass

    def testCreateUser(self):
        url = reverse('create-user')
        resp = self.client.post(url, {'username': 'hehe', 'password': 123}, format='json')       
        print(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('password'), None, 'no password, even if hashed, should be returned')

        implicit_default_organization = Organization.objects.get(name='hehe')
        self.assertNotEqual(implicit_default_organization, None, "An organization named 'hehe' with default=True should be created implicitly")

        resp = self.client.post(url, {'username': 'hehe', 'password': 123}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, "Create an existing user should return 400")

        url = reverse('login')
        resp = self.client.post(url, {'username': 'hehe', 'password': 123}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "Newly created user should be logged in without error")

        resp = self.client.post(url, {'username': 'hehe', 'password': 'wrongpass'}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, "Wrong password shoud return 400")

    def testRetrieveUser(self):
        create_url = reverse('create-user')
        resp = self.client.post(create_url, {'username': 'hehe', 'password': 123}, format='json')       

        retrieve_url = reverse('user-detail', kwargs={'pk': 1})
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.data['username'], 'hehe')

    def testPostInvalidUser(self):
        url = reverse('create-user')
        resp = self.client.post(url, {'username': 'u1', 'password': ''}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', resp.data['password'])
        
    def tearDown(self):
        pass
