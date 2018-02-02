from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django_client_logger.views import LogReceiver
import logging
import mock


class TestLoggerAPI(TestCase):
    def setUp(self):
        session = self.client.session
        session.save()

    def test_log_api(self):
        logger = logging.getLogger('TEST')
        with mock.patch.object(logger, 'info') as mock_logger:
            form = {'data': (
                '[{"logger": "TEST", "timestamp": 1517531326989, '
                '"level": "INFO", "message": ""}]')}
            response = self.client.post(reverse('client_log_api'), data=form)
            mock_logger.assert_called_once()

    def test_log_multiple_api(self):
        logger = logging.getLogger('TEST')
        with mock.patch.object(logger, 'info') as mock_logger:
            form = {'data': (
                '[{"logger": "TEST", "timestamp": 1517531326989, '
                '"level": "INFO", "message": ""},'
                '{"logger": "TEST", "timestamp": 1517531326999, '
                '"level": "INFO", "message": ""},'
                '{"logger": "TEST", "timestamp": 1517531327000, '
                ' "level": "INFO", "message": ""}]')}

            response = self.client.post(reverse('client_log_api'), data=form)
            self.assertEquals(mock_logger.call_count, 3)

    def test_log_error(self):
        logger = logging.getLogger('django_client_logger.views')
        with mock.patch.object(logger, 'error') as mock_logger:
            form = {'data': ''}
            response = self.client.post(reverse('client_log_api'), data=form)
            mock_logger.assert_called_once()
