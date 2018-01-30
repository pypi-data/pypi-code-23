from unittest import TestCase, skipIf
from restclients_core.dao import DAO
from os.path import abspath, dirname
from restclients_core.dao import MockDAO
from restclients_core.exceptions import DataFailureException


class TDAO(DAO):
    def service_name(self):
        return 'testing'

    def service_mock_paths(self):
        return [abspath(dirname(__file__) + "/resources/")]


class TestMock(TestCase):
    def test_found_resource(self):
        response = TDAO().getURL('/found.json', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.read(), '{"OK": true }\n')

    def test_missing_resource(self):
        response = TDAO().getURL('/missing.json', {})
        self.assertEquals(response.status, 404)

    def test_file_headers(self):
        response = TDAO().getURL('/with_headers.json', {})
        self.assertEquals(response.status, 202)

        self.assertEquals(response.headers["Custom"], "My Custom Value")
        self.assertEquals(response.getheader("Custom"), "My Custom Value")

    def test_plain_file_headers(self):
        response = TDAO().getURL('/with_only_headers.json', {})
        self.assertEquals(response.status, 200)

        self.assertEquals(response.headers["Custom2"], "My Custom Value 2")

    def test_registered_paths(self):
        response = TDAO().getURL('/override.json', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.read(), '{"override": false }\n')

        override = abspath(dirname(__file__) + "/resource_override/")
        MockDAO.register_mock_path(override)

        response = TDAO().getURL('/override.json', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.read(), '{"override": true }\n')

    def test_binary_data(self):
        response = TDAO().getURL('/image.jpg', {})
        self.assertEquals(response.status, 200)

    def test_out_of_order_params(self):
        response = TDAO().getURL('/search?'
                                 'first=a&second=b&third=c&fourth=d')
        self.assertEquals(response.status, 200)

    def test_extra_params(self):
        response = TDAO().getURL('/search?'
                                 'first=a&second=b&third=c&fourth=d&fifth=e')
        self.assertEquals(response.status, 404)

    def test_quoted_params(self):
        response = TDAO().getURL('/search?'
                                 'first=a&second=a%3Ab%3Ac')
        self.assertEquals(response.status, 200)

    def test_no_body_file(self):
        response = TDAO().getURL('/search?'
                                 'first=abc')
        self.assertEquals(response.status, 200)

    def test_multiple_files(self):
        with self.assertRaises(DataFailureException):
            TDAO().getURL('/search?'
                          'first=a&second=b')

    def test_quote_in_file_path(self):
        response = TDAO().getURL('/test%3folder/test.json')
        self.assertEquals(response.status, 200)

    def test_quote_in_file_path_and_file(self):
        response = TDAO().getURL('/test%3folder/test.json')
        self.assertEquals(response.status, 200)

    @skipIf(True, "I'm not sure that this case actually exists - ezturner")
    def test_quote_in_file_path_and_url_but_not_file(self):
        response = TDAO().getURL('/test%3folder/test%3man.json')
        self.assertEquals(response.status, 200)
