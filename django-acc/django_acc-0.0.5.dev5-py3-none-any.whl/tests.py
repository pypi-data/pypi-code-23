from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

# Create your tests here.
class IntegrationTest(APITestCase):
    def setUp(self):
        pass

    def testPostUser(self):
        url = reverse('accounts:create-user')
        resp = self.client.post(url, {'username': 'hehe', 'password': 123}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(url, {'username': 'hehe', 'password': 123}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, "Create a user already exists should return 400")

        url = reverse('accounts:login')
        resp = self.client.post(url, {'username': 'hehe', 'password': 123}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.post(url, {'username': 'hehe', 'password': 'wrongpass'}, format='json')       
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, "Wrong password shoud return 400")
        
    def tearDown(self):
        pass
