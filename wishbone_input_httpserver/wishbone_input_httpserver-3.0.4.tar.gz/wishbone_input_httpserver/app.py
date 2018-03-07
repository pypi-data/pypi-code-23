#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  app.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import falcon
from gevent import pywsgi
from gevent import socket
from gevent.pool import Pool
from wishbone_input_httpserver.middleware import GenerateMetaData
from wishbone_input_httpserver.middleware import BasicAuthentication
from wishbone_input_httpserver.middleware import TokenAuthentication
from wishbone_input_httpserver.middleware import Authorize
from wishbone_input_httpserver.middleware import DeriveQueue
from wishbone.error import ProtocolError, InvalidData


class LogWrapper(object):

    def __init__(self, wishbone_logger):

        self.logging = wishbone_logger

    def write(self, data):

        self.logging.info(data.rstrip())


class EventHandler(object):

    def __init__(self, decoder, wishbone_event_callback):

        self.decoder = decoder
        self.wishbone_event_callback = wishbone_event_callback

    def on_get(self, req, resp, queue="outbox"):

        if resp.status == "200 OK":
            try:
                response = self.wishbone_event_callback("", req.meta, req.queue)
                resp.body = response
            except InvalidData as err:
                resp.status = falcon.HTTP_400
                resp.body = "400 Bad Request. Unsupported event format. Reason: %s" % (err)

    def on_put(self, req, resp, queue="outbox"):

        if resp.status == "200 OK":
            try:
                for chunk in [req.stream, None]:
                    for item in self.decoder(chunk):
                        resp.body = self.wishbone_event_callback(item, req.meta, req.queue)
            except ProtocolError as err:
                resp.status = falcon.HTTP_406
                resp.body = "406 Not Acceptable. There was an error processing your request. Reason: ProtocolDecodeError %s" % str(err)
            except InvalidData as err:
                resp.status = falcon.HTTP_400
                resp.body = "400 Bad Request. Unsupported event format. Reason: %s" % (err)

    on_post = on_put


class FalconServer(object):

    def __init__(self, address, port, ssl_key, ssl_cert, ssl_cacerts, poolsize, so_reuseport,
                 callback_wishbone_event, wishbone_logger, wishbone_decoder, wishbone_queues,
                 callback_authorize_user, callback_authorize_token, callback_get_password_hash, callback_requires_authentication):

        self.address = address
        self.port = port
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.ssl_cacerts = ssl_cacerts
        self.poolsize = poolsize
        self.so_reuseport = so_reuseport
        self.callback_wishbone_event = callback_wishbone_event
        self.logger = wishbone_logger
        self.wishbone_decoder = wishbone_decoder
        self.wishbone_queues = wishbone_queues

        self.app = falcon.API(
            middleware=[
                DeriveQueue(
                    wishbone_queues
                ),
                BasicAuthentication(
                    callback_get_password_hash
                ),
                TokenAuthentication(
                ),
                Authorize(
                    callback_authorize_user,
                    callback_authorize_token,
                    callback_requires_authentication
                ),
                GenerateMetaData(
                )
            ]
        )

        event_handler = EventHandler(
            wishbone_decoder,
            callback_wishbone_event
        )

        self.app.add_route('/{queue}', event_handler)

        if self.ssl_key is not None and self.ssl_cert is not None:
            ssl_options = {
                "keyfile": self.ssl_key,
                "certfile": self.ssl_cert,
                "ca_certs": self.ssl_cacerts
            }
        else:
            ssl_options = {}

        self.server = pywsgi.WSGIServer(
            listener=self.__getListener(),
            application=self.app,
            spawn=Pool(self.poolsize),
            log=LogWrapper(self.logger),
            error_log=None,
            **ssl_options
        )

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def __getListener(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self.so_reuseport:
            sock.setsockopt(socket.SOL_SOCKET, 15, 1)

        sock.setblocking(0)
        sock.bind((self.address, self.port))
        sock.listen(50)
        return sock
