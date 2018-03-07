# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import logging
import socket
import threading
import time
import sys
import websocket
from six.moves import queue

from devicehive_plugin.api_handler import ApiHandler
from devicehive_plugin.error import TransportError
from devicehive_plugin.message import ResponseMessage


__all__ = ['Transport']
logger = logging.getLogger(__name__)


def _websocket_call(websocket_method, *args, **kwargs):
    try:
        return websocket_method(*args, **kwargs)
    except (websocket.WebSocketException, socket.error) as websocket_error:
        error = websocket_error
    raise TransportError(error)


class Transport(object):

    def __init__(self, api_handler_options):
        self._connected = False
        self._connection_lock = threading.Lock()
        self._websocket = websocket.WebSocket()
        self._connection_thread = None
        self._event_queue_sleep_time = None
        self._response_sleep_time = None
        self._exception_info = None
        self._event_queue = queue.Queue()
        self._api_handler = ApiHandler(self, **api_handler_options)
        self._responses = {}

    @property
    def exception_info(self):
        return self._exception_info

    @property
    def api_handler(self):
        return self._api_handler

    @property
    def connected(self):
        return self._connected
    
    def _ensure_not_connected(self):
        if not self._connected:
            return
        raise TransportError('Connection has already created.')

    def _ensure_connected(self):
        if self._connected:
            return
        raise TransportError('Connection has not created.')

    def _connection(self, url, options):
        try:
            self._connect(url, **options)
            self._receive()
            self._disconnect()
        except:
            self._exception_info = sys.exc_info()

    def connect(self, url, **options):
        self._ensure_not_connected()
        self._connection_thread = threading.Thread(target=self._connection,
                                                   args=(url, options))
        self._connection_thread.name = 'transport-connection'
        self._connection_thread.daemon = True
        self._connection_thread.start()

    def disconnect(self):
        self._ensure_connected()
        self._connected = False

    def is_alive(self):
        return self._connection_thread.is_alive()

    def _connect(self, url, **options):
        logger.debug('Connecting to %s', url)
        timeout = options.pop('timeout', None)
        event_queue_sleep_time = options.pop('event_queue_sleep_time', 1e-6)
        response_sleep_time = options.pop('response_sleep_time', 1e-6)
        pong_timeout = options.pop('pong_timeout', None)
        self._websocket.timeout = timeout
        self._event_queue_sleep_time = event_queue_sleep_time
        self._response_sleep_time = response_sleep_time
        _websocket_call(self._websocket.connect, url, **options)
        self._connected = True
        event_thread = threading.Thread(target=self._event)
        event_thread.name = 'transport-event'
        event_thread.daemon = True
        event_thread.start()

        if pong_timeout:
            ping_thread = threading.Thread(target=self._ping,
                                           args=(pong_timeout,))
            ping_thread.name = 'transport-ping'
            ping_thread.daemon = True
            ping_thread.start()
        self._handle_connect()
        logger.debug('Successfully connected')

    def _receive(self):
        while self._connected and not self._exception_info:
            if self._event_queue.empty():
                time.sleep(self._event_queue_sleep_time)
                continue

            event = self._event_queue.get()
            try:
                self._handle_event(event)
            finally:
                self._event_queue.task_done()

    def _disconnect(self):
        logger.debug('Disconnecting')
        _websocket_call(self._websocket.ping)
        with self._connection_lock:
            _websocket_call(self._websocket.close)
        self._pong_received = False
        self._responses = {}
        self._handle_disconnect()
        logger.debug('Successfully disconnected')

    def _handle_connect(self):
        self._api_handler.handle_connect()

    def _handle_event(self, event):
        self._api_handler.handle_event(event)

    def _handle_disconnect(self):
        self._api_handler.handle_disconnect()

    def _event(self):
        while self._connected:
            with self._connection_lock:
                opcode, data = _websocket_call(self._websocket.recv_data, True)
            if opcode in (websocket.ABNF.OPCODE_TEXT,
                          websocket.ABNF.OPCODE_BINARY):
                if opcode == websocket.ABNF.OPCODE_TEXT:
                    data = data.decode('utf-8')
                logger.debug('Event: %s', data)
                message = ResponseMessage(data)
                if not message.id:
                    self._event_queue.put(message)
                    continue
                self._responses[message.id] = message
                continue

            if opcode == websocket.ABNF.OPCODE_PONG:
                self._pong_received = True
                continue
            if opcode == websocket.ABNF.OPCODE_CLOSE:
                return

    def _ping(self, pong_timeout):
        while self._connected:
            try:
                _websocket_call(self._websocket.ping)
            except:
                self._connected = False
                return
            self._pong_received = False
            time.sleep(pong_timeout)
            if not self._pong_received:
                self._connected = False
                return

    def _request(self, request):
        request = request.encode()
        logger.debug('Request: %s', request)
        _websocket_call(self._websocket.send, request)

    def _receive_response(self, request_id, timeout):
        start_time = time.time()
        while time.time() - timeout < start_time:
            response = self._responses.get(request_id)
            if response:
                del self._responses[request_id]
                return response
            time.sleep(self._response_sleep_time)
        raise TransportError('Response timeout.')

    def async_request(self, request):
        self._ensure_connected()
        self._request(request)

    def request(self, request, timeout=30):
        self._ensure_connected()
        self._request(request)
        return self._receive_response(request.id, timeout)
