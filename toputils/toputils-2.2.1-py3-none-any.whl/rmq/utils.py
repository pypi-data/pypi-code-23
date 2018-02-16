# -*- coding: utf-8 -*-

"""
top_rmq.utils
~~~~~
Implements RMQConn object for publishing and consuming messages to/from
RabbitMQ queues.
:copyright: (c) 2017 Peter Schutt
"""


import configparser
import json
import logging
import pathlib
import ssl

import backoff
import pika

LOGGER = logging.getLogger(__name__)


def backoff_hdlr(d):
    LOGGER.debug(f"Backing off {d['wait']:0.1f} seconds after {d['tries']} "
                 f"tries calling function {d['target']} with args {d['args']} "
                 f"and kwargs {d['kwargs']}")


class RMQConn:
    """ Class that holds a connection to a RabbitMQ message queue and
    provides methods to connect, publish/consume and disconnect from
    a RabbitMQ server.
    Implements a context manager for easy connections and tidy closing.
    """
    def __init__(self, cnf_name, cnf_loc=None):
        """ Create RMQConn instance.
        :param cnf_identifier: Identifier string that designates desired
            configuration in configuration file.
        :param cnf_loc: (optional) Specify location of the configuration \
            file for the application.
            (default=pathlib.Path.home()}/.top_rmq/rmq.cnf)
        """
        self._conn = None
        cnf_loc = cnf_loc or f"{pathlib.Path.home()}/.toputils/rmq.local"
        cnf = configparser.ConfigParser()
        cnf.read(cnf_loc)
        self.params = cnf[cnf_name]
        self.conn_params_obj = self._get_conn_params()
        self.ex_params = self._get_exchange_params()
        self.b_params = self._get_bind_params()
        self.q_params = self._get_queue_params()
        self.pub_params = self._get_publish_params()

    def _get_conn_params(self):
        cred_params = {
            "username": self.params.get("username", "guest"),
            "password": self.params.get("password", "guest"),
        }
        cred_params = {k: v for k, v in cred_params.items() if v is not None}
        creds = pika.credentials.PlainCredentials(**cred_params)

        conn_params = {
            "host": self.params.get("host"),
            "port": self.params.get("port"),
            "virtual_host": self.params.get("virtual_host"),
            "channel_max": self.params.get("channel_max"),
            "frame_max": self.params.get("frame_max"),
            "heartbeat": self.params.get("heartbeat"),
            "ssl": self.params.getboolean("ssl"),
            "connection_attempts": self.params.get("connection_attempts"),
            "retry_delay": self.params.get("retry_delay"),
            "socket_timeout": self.params.get("socket_timeout"),
            "locale": self.params.get("locale"),
            "backpressure_detection": self.params.getboolean(
                "backpressure_detection"
            ),
            "blocked_connection_timeout": self.params.get(
                "blocked_connection_timeout"
            ),
            "client_properties": self.params.get("client_properties")
        }

        if conn_params["ssl"]:
            conn_params["port"] = 5671
            conn_params["ssl_options"] = {
                "keyfile": self.params.get("keyfile"),
                "certfile": self.params.get("certfile"),
                "ca_certs": self.params.get("ca_certs"),
                "ssl_version": ssl.PROTOCOL_TLSv1,
                "cert_reqs": ssl.CERT_REQUIRED
            }

        conn_params = {
            k: v for k, v in conn_params.items() if v is not None
        }

        for key in ("port", "channel_max", "frame_max", "heartbeat",
                    "connection_attempts", "blocked_connection_timeout"):
            try:
                conn_params[key] = int(conn_params[key])
            except KeyError:
                pass

        for key in ("retry_delay", "socket_timeout"):
            try:
                conn_params[key] = float(conn_params[key])
            except KeyError:
                pass

        conn_params["credentials"] = creds

        return pika.ConnectionParameters(**conn_params)

    def _get_exchange_params(self):
        ex_params = {
            "exchange": self.params.get("exchange"),
            "exchange_type": self.params.get("exchange_type"),
            "passive": self.params.getboolean("ex_passive"),
            "durable": self.params.getboolean("ex_durable"),
            "auto_delete": self.params.getboolean("ex_auto_delete"),
            "internal": self.params.getboolean("internal"),
            "nowait": self.params.getboolean("ex_nowait"),
            "arguments": self.params.get("ex_arguments")
        }

        ex_params = {k: v for k, v in ex_params.items() if v is not None}

        try:
            ex_params["arguments"] = json.loads(ex_params["arguments"])
        except KeyError:
            pass

        return ex_params

    def _get_queue_params(self):
        q_params = {
            "queue": self.params.get("queue"),
            "passive": self.params.getboolean("q_passive"),
            "durable": self.params.getboolean("q_durable"),
            "exclusive": self.params.getboolean("exclusive"),
            "auto_delete": self.params.getboolean("q_auto_delete"),
            "nowait": self.params.getboolean("q_nowait"),
            "arguments": self.params.get("q_arguments")
        }

        q_params = {k: v for k, v in q_params.items() if v is not None}

        try:
            q_params["arguments"] = json.loads(q_params["arguments"])
        except KeyError:
            pass

        return q_params

    def _get_publish_params(self):
        pub_params = {
            "routing_key": self.params.get("routing_key"),
            "mandatory": self.params.getboolean("mandatory"),
            "immediate": self.params.getboolean("immediate")
        }
        pub_params = {k: v for k, v in pub_params.items() if v is not None}
        properties = {
            "content_type": self.params.get("content_type"),
            "content_encoding": self.params.get("content_encoding"),
            "headers": self.params.get("headers"),
            "delivery_mode": self.params.get("delivery_mode"),
            "priority": self.params.get("priority")
        }
        properties = {k: v for k, v in properties.items() if v is not None}
        try:
            properties['delivery_mode'] = int(properties['delivery_mode'])
        except KeyError:
            pass
        pub_params["properties"] = pika.BasicProperties(**{
            k: v for k, v in properties.items() if v is not None
        })
        return pub_params

    def _get_bind_params(self):
        b_params = {
            "nowait": self.params.get("b_nowait"),
            "arguments": self.params.get("b_arguments")
        }
        b_params = {k: v for k, v in b_params.items() if v is not None}
        try:
            b_params["arguments"] = json.loads(b_params["arguments"])
        except KeyError:
            pass
        return b_params

    @backoff.on_exception(backoff.expo,
                          pika.exceptions.ConnectionClosed,
                          max_tries=5,
                          on_backoff=backoff_hdlr)
    def connect(self):
        """ Connect to RabbitMQ server with designated configuration,
        create channel and bind channel to queue."""
        self._conn = pika.BlockingConnection(self.conn_params_obj)
        self._channel = self._conn.channel()
        self._channel.queue_declare(**self.q_params)
        self._channel.confirm_delivery()
        self._channel.exchange_declare(**self.ex_params)
        self._channel.queue_bind(
            queue=self.q_params.get("queue"),
            exchange=self.ex_params.get("exchange"),
            routing_key=self.pub_params.get("routing_key"),
            **self.b_params
        )

    def close(self):
        """Close channel and connection if they have been established."""

        if self._channel is not None:
            try:
                self._channel.close()
            except (pika.exceptions.ChannelClosed,
                    pika.exceptions.ChannelAlreadyClosing):
                pass
        if self._conn is not None:
            self._conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    @backoff.on_exception(backoff.expo,
                          pika.exceptions.NackError,
                          max_tries=5,
                          on_backoff=backoff_hdlr)
    def publish(self, msg):
        """ publish message to queue and log confirmation of delivery"""

        if self._channel.basic_publish(
            exchange=self.ex_params.get("exchange"),
            body=msg,
            **self.pub_params
        ):
            LOGGER.info('Message publish was confirmed')
        else:
            LOGGER.warning('Message could not be confirmed')
