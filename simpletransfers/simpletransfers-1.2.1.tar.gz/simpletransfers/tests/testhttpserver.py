from __future__ import absolute_import, print_function, unicode_literals
import unittest
from flask import Flask

from ..http_server import http_server, wsgi_interface

post_xml = '<?xml version="1.0"?><test><element attrib="value" /></test>'
post_json = '{"test": {"element": {"@attrib": "value"}}}'
get_json = '[{ "serial": "0123456776543210", "pin":1234 }]'


class testHTTPServer(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.config[ 'TESTING' ] = True

        app.add_url_rule(
            '/testpost', 'post', self._post, methods = [ 'POST' ]
        )
        app.add_url_rule('/testget', 'get', self._get)
        app.add_url_rule(
            '/testget/serial/<serial>', 'get', self._get
        )

        self.app = app.test_client()

    @wsgi_interface
    def _post(self):
        receiver = http_server()
        self.assertEquals(
            receiver.get()[ '_raw' ], post_xml
        )
        receiver.put(post_json, 'response.json')

    @wsgi_interface
    def _get(self):
        receiver = http_server()
        self.assertEquals(
            receiver.get()[ 'serial' ], '0123456776543210'
        )
        receiver.put(get_json, 'response.json')

    def test_post(self):
        response = self.app.post(
            '/testpost', data = post_xml, content_type = 'text/xml'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.headers['Content-Type'], 
            'application/json'
        )
        self.assertEquals(response.get_data(), post_json)

    def test_get(self):
        response = self.app.get('/testget/serial/0123456776543210')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.headers['Content-Type'], 
            'application/json'
        )
        self.assertEquals(response.get_data(), get_json)

        # test request via traditional query string too
        response = self.app.get('/testget?serial=0123456776543210')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.headers['Content-Type'], 
            'application/json'
        )
        self.assertEquals(response.get_data(), get_json)

    def test_incorrect_path(self):
        response = self.app.get('/tests/doesnotexist')
        self.assertEquals(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
