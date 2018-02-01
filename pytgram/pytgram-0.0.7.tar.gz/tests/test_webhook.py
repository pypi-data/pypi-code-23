import json
from io import BytesIO

from twisted.trial import unittest
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.web.server import Site
from twisted.web.client import Agent, FileBodyProducer

from pytgram.api import _HTTPClientProtocol
from pytgram.content import Message
from pytgram.webhook import (
    web_hook, _RootResource, _BotResource, set_webhook, delete_webhook,
    get_webhook_info
)
from tests import TOKEN, WEB_HOOK_URL


class TestWebHook(unittest.TestCase):

    def setUp(self):
        self.root = _RootResource()
        self.root.putChild('path', _BotResource())
        self.port = reactor.listenTCP(80, Site(self.root))

    def tearDown(self):
        reactor.removeAll()
        return self.port.stopListening()

    @staticmethod
    def request(url, method, deferred, **kwargs):
        body = None
        if kwargs:
            body = FileBodyProducer(BytesIO(json.dumps(kwargs).encode()))
        args = {'uri': url.encode(), 'method': method.encode(),
                'bodyProducer': body}
        resp_def = Agent(reactor).request(**args)

        def get_body(response, dfd):
            response.deliverBody(_HTTPClientProtocol(dfd))

        resp_def.addCallback(get_body, deferred)
        return resp_def

    def test_web_hook(self):
        def handler():
            pass
        path = 'some_url_path'
        site = web_hook(path, handler)
        self.assertIsInstance(site, Site)
        self.assertIsInstance(site.resource, _RootResource)
        self.assertIsInstance(site.resource.children[path], _BotResource)

    def test_set_web_hook(self):
        response = set_webhook(TOKEN, WEB_HOOK_URL)
        self.assertIsInstance(response, dict)
        self.assertIs(response['result'], True)

    def test_set_web_hook_fail(self):
        response = set_webhook('some_token', 'https://test.py/path')
        self.assertIs(response['ok'], False)
        self.assertEqual(response['error_code'], 404)

    def test_delete_web_hook(self):
        response = delete_webhook(TOKEN)
        self.assertIs(response['result'], True)

    def test_delete_web_hook_fail(self):
        response = delete_webhook('some_token')
        self.assertIs(response['ok'], False)
        self.assertEqual(response['error_code'], 404)

    def test_get_web_hook_info(self):
        response = get_webhook_info(TOKEN)
        self.assertIsInstance(response['result'], dict)

    def test_get_web_hook_info_fail(self):
        response = get_webhook_info('some_token')
        self.assertIs(response['ok'], False)
        self.assertEqual(response['error_code'], 404)

    def test_root_resource_valid_child(self):
        deferred = Deferred()

        def check_assert(response):
            body = json.loads(response.decode())
            self.assertEqual(body['code'], 400)

        deferred.addCallback(check_assert)
        self.request('http://127.0.0.1/path', 'POST', deferred)
        return deferred

    def test_root_resource_invalid_child(self):
        deferred = Deferred()

        def check_assert(response):
            body = json.loads(response.decode())
            self.assertEqual(body['code'], 404)

        deferred.addCallback(check_assert)
        self.request('http://127.0.0.1/invalid_path', 'POST', deferred)
        return deferred

    def test_root_resource_invalid_method(self):
        deferred = Deferred()

        def check_assert(response):
            body = json.loads(response.decode())
            self.assertEqual(body['code'], 405)

        deferred.addCallback(check_assert)
        self.request('http://127.0.0.1/path', 'GET', deferred)
        return deferred

    def test_bot_resource(self):
        deferred = Deferred()

        args = {'message': {'message_id': 5102,
                            'date': 14925053,
                            'chat': {'id': 72340936, 'type': 'private',
                                     'first_name': ''},
                            'from': {'id': 72340936, 'first_name': 'Artem'},
                            'text': 'asdsadg'}
                }

        def check_response_assert(response):
            self.assertEqual(response.decode(), '')

        def check_message_assert(message):
            self.assertIsInstance(message, Message)

        self.root.children['path']._handler = check_message_assert
        deferred.addCallback(check_response_assert)
        self.request('http://127.0.0.1/path', 'POST', deferred, **args)
        return deferred
