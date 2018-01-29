#!/usr/bin/env python
# coding=utf-8

import json
import sys
import threading
import time

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet import reactor, ssl
from twisted.internet.error import ReactorAlreadyRunning
from twisted.python import log


# ----- twisted ----------
class _WebSocketClientProtocol(WebSocketClientProtocol):
    def __init__(self, factory):
        super(_WebSocketClientProtocol, self).__init__()
        self.factory = factory

    def onOpen(self):
        print("Client connected")
        self.factory.protocol_instance = self
        self.factory.base_client._connected_event.set()

    def onMessage(self, payload, isBinary):
        print(payload)
        if not isBinary:
            payload_obj = json.loads(payload.decode('utf8'))
            self.factory.callback(payload_obj)

class _WebSocketClientFactory(WebSocketClientFactory):
    def __init__(self, *args, **kwargs):
        WebSocketClientFactory.__init__(self, *args, **kwargs)
        self.protocol_instance = None
        self.base_client = None

    def buildProtocol(self, addr):
        return _WebSocketClientProtocol(self)
# ------ end twisted -------


class BaseWBClient(object):

    STREAM_URL = 'wss://api.idex.market'

    def __init__(self):
        # instance to be set by the own factory
        self.factory = None
        # this event will be triggered on onOpen()
        self._connected_event = threading.Event()
        self._reactor_thread = None

    def connect(self):
        print("Connecting to {}".format(self.STREAM_URL))
        log.startLogging(sys.stdout)
        self.factory = _WebSocketClientFactory(self.STREAM_URL)
        self.factory.base_client = self
        context_factory = ssl.ClientContextFactory()
        c = connectWS(self.factory, context_factory)
        self._reactor_thread = threading.Thread(target=reactor.run, args=(False,))
        self._reactor_thread.daemon = True
        self._reactor_thread.start()

    def send_message(self, body):
        if not self._check_connection():
            return
        print("sending")
        reactor.callFromThread(self._dispatch, body)

    def _check_connection(self):
        while not self.factory.protocol_instance:
            time.sleep(1)
            print("Unable to connect to server")
            #self.close()
            #return False
        return True

    def _dispatch(self, body):
        print("Dispatching")
        self.factory.protocol_instance.sendMessage(body)

    def close(self):
        reactor.callFromThread(reactor.stop)
