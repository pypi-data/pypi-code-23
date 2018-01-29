#!/usr/bin/env python
# coding=utf-8

import json
import sys
import threading

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet import reactor, ssl
from twisted.internet.error import ReactorAlreadyRunning
from twisted.python import log


class IdexClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Client connected")

    def onOpen(self):
        print("Client open")
        self.factory.protocol_instance = self

    def onMessage(self, payload, isBinary):
        pass
        #print(payload)
        #if not isBinary:
        #    payload_obj = json.loads(payload.decode('utf8'))
        #    self.factory.callback(payload_obj)

    def onClose(self, wasClean, code, reason):
        if wasClean:
            print("was clean close")
        else:
            print("was not clean close")

        print("code:{} reason:{}".format(code, reason))


class IdexClientFactory(WebSocketClientFactory):
    def __init__(self, *args, **kwargs):
        WebSocketClientFactory.__init__(self, *args, **kwargs)
        self.protocol_instance = None

    def buildProtocol(self, *args, **kwargs):
        return IdexClientFactory(self)


class IdexSocketClass(IdexClientProtocol):

    STREAM_URL = 'wss://api.idex.market'
    #STREAM_URL = 'wss://idex.market/ws'

    def __init__(self):
        self._factory = WebSocketClientFactory(self.STREAM_URL)
        log.startLogging(sys.stdout)
        self._factory.protocol = IdexClientProtocol
        context_factory = ssl.ClientContextFactory()
        self._conn = connectWS(self._factory, context_factory)
        reactor.run(installSignalHandlers=0)


class IdexSocketManager(threading.Thread):

    STREAM_URL = 'wss://api.idex.market/'

    def __init__(self):
        """Initialise the IdexSocketManager

        """
        threading.Thread.__init__(self)
        self._conn = None
        self._markets = []
        self._callbacks = {}
        self._factory = None

        log.startLogging(sys.stdout)

        self._init_socket()

    def _init_socket(self):
        self._factory = WebSocketClientFactory(self.STREAM_URL)
        self._factory.protocol = IdexClientProtocol
        self._factory.callback = self._socket_callback
        context_factory = ssl.ClientContextFactory()

        self._conn = connectWS(self._factory, context_factory)

    def _socket_callback(self, evt):
        if 'topic' in evt and evt['topic'] in self._markets:
            # check for error
            if 'error' in evt['message']:
                print(evt['message']['error'])
                pass
            else:
                self._callbacks[evt['topic']](evt['topic'], evt['message'])

    def _start_socket(self, path):

        msg = json.dumps({"subscribe": path}).encode('utf-8')
        print(msg)
        #self._factory.protocol_instance.sendMessage(msg, False)
        #self._conn.subscribe(self._socket_callback, path)

    def start_market_socket(self, market, callback):
        """Start a websocket for symbol market depth

        https://www.binance.com/restapipub.html#depth-wss-endpoint

        :param market: required e.g. ETH_DIVP
        :type market: str
        :param callback: callback function to handle messages
        :type callback: function

        :returns: True successful, False otherwise

        Message Format

        .. code-block:: python

            {
                "e": "depthUpdate",			# event type
                "E": 1499404630606, 		# event time
                "s": "ETHBTC", 				# symbol
                "u": 7913455, 				# updateId to sync up with updateid in /api/v1/depth
                "b": [						# bid depth delta
                    [
                        "0.10376590", 		# price (need to update the quantity on this price)
                        "59.15767010", 		# quantity
                        []					# can be ignored
                    ],
                ],
                "a": [						# ask depth delta
                    [
                        "0.10376586", 		# price (need to update the quantity on this price)
                        "159.15767010", 	# quantity
                        []					# can be ignored
                    ],
                    [
                        "0.10383109",
                        "345.86845230",
                        []
                    ],
                    [
                        "0.10490700",
                        "0.00000000", 		# quantity=0 means remove this level
                        []
                    ]
                ]
            }
        """
        if market in self._markets:
            return False

        self._markets.append(market)
        self._callbacks[market] = callback
        self._start_socket(market)
        return True

    def stop_market_socket(self, market):
        if market not in self._markets:
            return False

        self._conn.unsubcribe(market)
        self._markets.remove(market)
        del(self._callbacks[market])
        return True

    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass