from __future__ import absolute_import, print_function, unicode_literals
import json

from stubserver import StubServer
import unittest

from ..http_client import http_client, TransferException

test_json = json.dumps({ 'quantity': 5 })

class testHTTPClient(unittest.TestCase):

    def setUp(self):
        self.server = StubServer(8095)
        self.server.run()

    def tearDown(self):
        self.server.stop()

    def test_get(self):
        self.server.expect(
            method = "GET",
            url = "/pin/serial/\d+$",
        ).and_return(
            content = test_json,
            mime_type = "application/json",
        )

        obj = http_client('http://localhost:8095/pin/serial/658329293232')
        contents = obj.get()

        result = json.loads(contents[ '658329293232' ])
        self.assertEquals(5, result[ 'quantity' ])

    def test_post(self):
        capture = {}
        self.server.expect(
            method = "POST",
            url = "/serial",
            data_capture = capture,
        ).and_return(reply_code = 200)

        obj = http_client('http://localhost:8095/serial')
        obj.put(json.dumps({ 'quantity': 5 }))

        result = json.loads(capture[ 'body' ])
        self.assertEquals(5, result[ 'quantity' ])

    def test_with_500(self):
        capture = {}
        self.server.expect(
            method = "POST",
            url = "/allocate",
            data_capture = capture
        ).and_return(reply_code = 500)

        obj = http_client('http://localhost:8095/allocate')
        self.assertRaises(TransferException, obj.put, test_json)

if __name__ == '__main__':
    unittest.main()
