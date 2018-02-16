# -*- coding: utf-8 -*-

"""
tests.rmq_tests.py
~~~~~~~~~~~~~

Tests for toputils.rmq

:copyright: (c) 2017 Peter Schutt
"""
import logging
import os
from unittest.mock import Mock, patch

import pika

import toputils.rmq as rmq

CWD = os.path.abspath(os.path.dirname(__file__))
CNF_PATH = CWD + "/rmq_test.cnf"

logging.basicConfig(level=logging.DEBUG)


def setup_module():

    with open(CNF_PATH, "w") as f:
        f.write("""
[cnf_identifier]
host = 0.0.0.0
port = 5672
ca_certs = /dir/to/ca.pem
certfile = /dir/to/client-cert.pem
keyfile = /dir/to/client-key.pem
username = user-name
password = password1
queue = queue_name
exchange = exchange_name
exchange_type = direct
routing_key = routing_key
content_type = text

[cnf_identifier_2]
host = localhost
port = 5672
ssl = True
username = user-name
password = password1
queue = queue_name
exchange = exchange_name
exchange_type = direct
ca_certs = /dir/to/ca.pem
certfile = /dir/to/client-cert.pem
keyfile = /dir/to/client-key.pem
routing_key = routing_key
content_type = text
""")


def teardown_module():
    try:
        os.remove(CNF_PATH)
    except OSError:
        pass


def test_instantiation():
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    assert type(r) == rmq.RMQConn
    r = rmq.RMQConn("cnf_identifier_2", CNF_PATH)
    assert type(r) == rmq.RMQConn


def test_conn_param_obj():
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    assert type(r.conn_params_obj) == pika.ConnectionParameters
    assert r.conn_params_obj.host == "0.0.0.0"
    assert r.conn_params_obj.port == 5672
    assert (type(r.conn_params_obj.credentials) ==
            pika.credentials.PlainCredentials)
    assert r.conn_params_obj.credentials.username == "user-name"
    assert r.conn_params_obj.credentials.password == "password1"
    # if ssl false then shouldn't parse the encryption certs
    assert r.conn_params_obj.ssl is False
    assert r.conn_params_obj.ssl_options is None
    r = rmq.RMQConn("cnf_identifier_2", CNF_PATH)
    assert type(r.conn_params_obj.ssl_options) == dict
    assert r.conn_params_obj.ssl_options["ca_certs"] == "/dir/to/ca.pem"
    assert (r.conn_params_obj.ssl_options["certfile"] ==
            "/dir/to/client-cert.pem")
    assert (r.conn_params_obj.ssl_options["keyfile"] ==
            "/dir/to/client-key.pem")
    # even though port in cnf in 5672, ssl is specified
    assert r.conn_params_obj.port == 5671


def test_exchange_params():
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    assert "exchange" in r.ex_params
    assert "exchange_type" in r.ex_params
    assert r.ex_params["exchange"] == "exchange_name"
    assert r.ex_params["exchange_type"] == "direct"


def test_queue_params():
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    assert "queue" in r.q_params
    assert r.q_params["queue"] == "queue_name"


def test_publish_params():
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    assert "routing_key" in r.pub_params
    assert r.pub_params["routing_key"] == "routing_key"
    assert "properties" in r.pub_params
    assert type(r.pub_params["properties"]) == pika.BasicProperties


def test_bind_params():
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    assert r.b_params == {}


@patch('pika.BlockingConnection')
def test_connect(mock):
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    r.connect()
    assert pika.BlockingConnection.call_count == 1
    r._conn.channel.assert_called_once_with()
    r._channel.queue_declare.assert_called_once_with(queue="queue_name")
    r._channel.confirm_delivery.assert_called_once_with()
    r._channel.exchange_declare.assert_called_once_with(
        exchange="exchange_name",
        exchange_type="direct"
    )
    r._channel.queue_bind.assert_called_once_with(
        queue="queue_name",
        exchange="exchange_name",
        routing_key="routing_key"
    )


@patch('pika.BlockingConnection')
def test_close(mock):
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    r.connect()
    r.close()
    r._channel.close.assert_called_once_with()
    r._conn.close.assert_called_once_with()


@patch('pika.BlockingConnection')
def test_publish(mock):
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    msg = "a message"
    r.connect()
    r.publish(msg)
    r._channel.basic_publish.assert_called_once_with(
        exchange="exchange_name",
        body=msg,
        routing_key="routing_key",
        properties=r.pub_params['properties']
    )
    args, kwargs = r._channel.basic_publish.call_args
    assert kwargs['properties'].content_type == "text"


@patch('pika.BlockingConnection')
def test_context_manager(mock):
    with rmq.RMQConn("cnf_identifier", CNF_PATH) as r:
        r.publish("a message")

    pika.BlockingConnection.call_count == 1
    r._channel.close.assert_called_once_with()
    r._conn.close.assert_called_once_with()


@patch('pika.BlockingConnection')
def test_publish_retries(mock):
    r = rmq.RMQConn("cnf_identifier", CNF_PATH)
    r.connect()
    r._channel.basic_publish = Mock()
    r._channel.basic_publish.side_effect = pika.exceptions.NackError("argh")
    try:
        r.publish("message")
    except pika.exceptions.NackError:
        pass
    assert r._channel.basic_publish.call_count == 5
