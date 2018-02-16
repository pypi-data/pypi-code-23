from django.test import TestCase
from django.test import Client
from django.conf import settings
from email.mime.text import MIMEText
from .views import calfile
from .utils import get_cal_serialize_file, get_part

class ViewTestCase(TestCase):
    def test_view(self):
        response = self.client.get('/calfile/')
        self.assertEqual(response.status_code, 405, "Get not allowed")

        with self.assertRaises(KeyError):
            self.client.post('/calfile/', {'start_date': '', 'end_date': ''})
        with self.assertRaises(ValueError):
            self.client.post('/calfile/', {'start_date': 'x', 'end_date': 'y'})

        test_params = {'start_date': '1-1-2018 13:00', 'end_date': '1-1-2018 14:30'}
        settings.CALFILE_DF = "%d-%m-%Y"

        with self.assertRaises(ValueError):
             self.client.post('/calfile/', test_params)

        settings.CALFILE_DF = "%d-%m-%Y %H:%M"
        response = self.client.post('/calfile/', test_params)
        self.assertEqual(response.status_code, 200, "Post error")

class UtilsTestCase(TestCase):
    def test_get_cal_serialize_file(self):
        start_date=''
        end_date=''
        with self.assertRaises(KeyError):
            get_cal_serialize_file(start_date, end_date, "")

        start_date='1-1-2018 13:00'
        end_date = '1-1-2018 14:30'
        result = get_cal_serialize_file(start_date, end_date, "")
        self.assertTrue(result)

    def test_get_part(self):
        
        start_date='1-1-2018 13:00'
        end_date = '1-1-2018 14:30'
        result = get_part(start_date, end_date, "")
        
        self.assertTrue(isinstance(result, MIMEText))