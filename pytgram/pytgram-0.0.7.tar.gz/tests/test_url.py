from unittest import TestCase

from pytgram.url import get_url


class TestURL(TestCase):

    def test_method(self):
        url = get_url(token='some_token', method='some_method')
        self.assertEqual(url,
                         'https://api.telegram.org/botsome_token/some_method')

    def test_file(self):
        url = get_url(url_type='file', token='some_token', path='some_path')
        self.assertEqual(url, 'https://api.telegram.org/'
                              'file/botsome_token/some_path')

    def test_without_args_method(self):
        url = get_url()
        self.assertEqual(url, 'https://api.telegram.org/bot{token}/{method}')

    def test_without_args_file(self):
        url = get_url(url_type='file')
        self.assertEqual(url,
                         'https://api.telegram.org/file/bot{token}/{path}')
