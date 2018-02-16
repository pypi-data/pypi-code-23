# -*- coding: utf-8 -*-

"""
toputils.rmq
============

Boilerplate for publishing and (soon) consuming off RabbitMQ Queues.

User can create the RMQConn object themselves and be responsible
for managing the connect() and close() methods however it's preferrable
to use the context manager functionality wherever possible.

All necessary parameters are established in a configuration file. The
following example lists all possible parameters and the default values
that pika carries for each. All can be individually set for a connection
but this is an exhaustive list and much of the time the defaults will do.
The ``[cnf_identifier]`` is the string passed to the RMQConn constructor
which allows it to identify the configuration setup you are using for
the connection. The cnf file can contain multiple sections for
connections to different queues, each just needs it's own
``[cnf_identifier]`` header. Uncomment out and change any of the
following::

    [cnf_identifier]

    ### CONNECTION PARAMETERS ###
    ## see :class:`pika.connection.ConnectionParameters ##
    # host = localhost
    # port = 5672
    # virtual_host = /
    # username = guest
    # password = guest
    # channel_max = 65535
    # frame_max = 131072
    # heartbeat
    # ssl = False
    # connection_attempts = 1
    # retry_delay = 2.0
    # socket_timeout = 0.25
    # locale = en_US
    # backpressure_detection = False
    # blocked_connection_timeout
    # client_properties
    ## these will only be searched if ssl = True
    ## specify path for each
    # keyfile
    # certfile
    # ca_certs

    ### QUEUE PARAMETERS ###
    ## see :meth:`pika.channel.Channel.queue_declare` ##
    # queue =
    # q_passive = False
    # q_durable = False
    # exclusive = False
    # q_auto_delete = False
    # q_nowait = False
    # q_arguments

    ### EXCHANGE PARAMETERS ###
    ## see :meth:`pika.channel.Channel.exchange_declare` ##
    # exchange
    # exchange_type = direct
    # ex_passive = False
    # ex_durable = False
    # ex_auto_delete = False
    # internal = False
    # ex_nowait = False
    # ex_arguments

    ### BIND PARAMETERS ###
    ## see :meth:`pika.channel.Channel.exchange_bind` ##
    # b_nowait = False
    # b_arguments

    ### PUBLISH PARAMETERS ###
    ## see :meth:`pika.channel.Channel.basic_publish` ##
    # routing_key =
    # mandatory = False
    # immediate = False

    ### BASIC PROPERTIES PARAMETERS ###
    ## see :class:`pika.spec.BasicProperties` ##
    # content_type
    # content_encoding
    # headers
    # delivery_mode
    # priority


Example Usage::

    >>> from toputils.rmq import RMQConn
    >>> with RMQConn("cnf_identifier") as r:
    ...     r.publish('{"some": "message"}')

:copyright: (c) 2017 Peter Schutt
"""

from .utils import RMQConn

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
