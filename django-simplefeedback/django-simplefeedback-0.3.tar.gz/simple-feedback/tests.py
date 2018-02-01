from django.contrib.auth.models import User
from django.core import mail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient


class TestTicketAPI(APITestCase):
    PASSWORD = 'secret'

    def setUp(self):
        super().setUp()

        # Create users
        self.user = User.objects.create_user('user@random.com', email='user@random.com', password=self.PASSWORD)
        self.admin = User.objects.create_superuser('admin@business.com', email='admin@business.com',
                                                   password=self.PASSWORD)

        # Set clients
        self.user_client = APIClient()
        self.user_client.login(username='user@random.com', password=self.PASSWORD)
        self.anon_client = APIClient()

    def test_create_user_ticket(self):
        url = reverse('ticket-create')
        data = {
            'subject': 'Hello',
            'text': 'I have a problem',
            'meta': {
                'page': '/blog/1'
            }
        }
        response = self.user_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['text'], 'I have a problem')
        self.assertEqual(response.data['assignee'], None)

    def test_create_user_ticket_text_required(self):
        url = reverse('ticket-create')
        data = {
            'subject': 'Hello',
        }
        response = self.user_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'text': ['This field is required.']})

    def test_create_user_ticket_subject_required(self):
        url = reverse('ticket-create')
        data = {
            'text': 'I have a problem',
        }
        response = self.user_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'subject': ['This field is required.']})

    def test_create_anonym_ticket(self):
        url = reverse('ticket-create')
        data = {
            'email': 'anonym@mail.com',
            'subject': 'Hello',
            'text': 'I have a problem',
            'meta': {
                'page': '/blog/1'
            }
        }
        response = self.anon_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user'], None)
        self.assertEqual(response.data['text'], 'I have a problem')

    def test_create_user_ticket_notify_superusers(self):
        url = reverse('ticket-create')
        data = {
            'subject': 'Hello',
            'text': 'I have a problem',
            'meta': {
                'page': '/blog/1'
            }
        }
        response = self.user_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(mail.outbox[0].subject, 'New ticket has been submitted')
        self.assertIn('I have a problem', mail.outbox[0].message().as_string())
