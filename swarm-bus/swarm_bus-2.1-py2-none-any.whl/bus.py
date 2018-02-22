"""
Client to connect to AMQP.
"""
import logging
import os
import socket
import time
from datetime import datetime

from kombu import Connection
from kombu import Exchange
from kombu import Queue

from swarm_bus.patching import fix_libs
from swarm_bus.settings import settings


fix_libs()

logger = logging.getLogger(__name__)


class AMQP(object):
    """
    Base client for AMQP.

    Implementing topic exchange on a queue.

    Can be used as a Producer:

    producer = AMQP()
    producer.connect()
    producer.publish('swarm.title.update', {'id': 42})
    producer.close()

    Can be used as a Consumer:

    def title_create(body, message):
        id_ = body['id']
        rk = message.delivery_info['routing_key']
        print("[x] %r:%r" % (rk, id_))

    def title_update(body, message):
        id_ = body['id']
        rk = message.delivery_info['routing_key']
        print("[x] %r:%r" % (rk, id_))
        message.ack()

    consumer = AMQP()
    consumer.connect()
    try:
        consumer.consume('queue', title_create, title_update)
    finally:
        consumer.close()
    """

    def __init__(self, **kwargs):
        self.uri = settings.amqp['URI']
        self.office_hours = settings.amqp['OFFICE_HOURS']
        self.transport_options = settings.amqp['TRANSPORT'].copy()
        self.queues = settings.amqp['QUEUES']

        if self.transport_options.get('queue_name_prefix'):
            queue_prefix = self.transport_options['queue_name_prefix']
            queue_prefix = queue_prefix % {'hostname': self.get_hostname()}
            self.transport_options['queue_name_prefix'] = queue_prefix

        self.raven = kwargs.pop('raven', None)

        self.exchange = None
        self.connection = None

    def __del__(self):
        """
        Close the connection when garbage collected.
        """
        self.close()

    def __enter__(self):
        """
        Context manager establishing connection.
        """
        self.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Context manager closing connection.
        """
        self.close()

    def get_hostname(self):
        """
        Method for having consistent hostname accros Docker images
        """
        default = socket.gethostname()
        hostname = os.getenv('AMQP_HOSTNAME', default)
        return hostname

    def connect(self):
        """
        Connects to the AMQP server and setup the exchange.
        """
        self.connection = Connection(
            self.uri,
            transport_options=self.transport_options)
        self.connection.connect()
        logger.info("[AMQP] Connected to %s, using '%s' prefix",
                    self.connection.as_uri(),
                    self.transport_options['queue_name_prefix'][:-1])

        self.declare()

    def declare(self):
        """
        Declare exchange and all queues with routing keys.
        """
        self.exchange = Exchange('swarm', 'topic')
        self.exchange(self.connection).declare()

        for queue_name, queue_attrs in self.queues.items():
            for routing_key in queue_attrs['routes']:
                queue = Queue(queue_name,
                              exchange=self.exchange,
                              routing_key=routing_key)
                queue(self.connection).declare()

    def close(self):
        """
        Close the connection.
        """
        if self.connection:
            self.connection.release()
            self.connection = None
            logger.info('[AMQP] Disconnected')

    def callback_wrapper(self, callback):
        """
        Decorate the callback to log exceptions
        and send them to Senty later if possible.

        Also cancels the exception to avoid process to crash !
        """
        def exception_catcher(body, message):
            """
            Decorator around callback.
            """
            try:
                return callback(body, message)
            except Exception:
                logger.exception('[AMQP] Unhandled exception occured !')
                if self.raven:
                    self.raven.captureException()

        return exception_catcher

    @property
    def can_consume(self):
        if not self.office_hours:
            return True

        now = datetime.now()
        if now.weekday() in [5, 6]:  # Week-end
            return False

        hour = now.hour
        if hour >= 9 and hour < 20:
            return True

        return False

    def consume(self, queue_name, *callbacks):
        """
        Starts the processing of a queue.
        """
        if queue_name not in self.queues:
            raise ValueError("'%s' is an unknown queue" % queue_name)

        if self.connection is None:
            self.connect()

        queue = Queue(queue_name, exchange=self.exchange)

        callbacks = [self.callback_wrapper(cb) for cb in callbacks]

        with self.connection.Consumer(
                queues=[queue], callbacks=callbacks):
            while True:
                if self.can_consume:
                    self.connection.drain_events()
                time.sleep(self.queues[queue_name].get('sleep', 0))

    def publish(self, routing_key, datas=None):
        """
        Publish datas on exchange using routing_key.
        """
        if datas is None:
            return

        if self.connection is None:
            self.connect()

        with self.connection.Producer() as producer:
            producer.publish(datas,
                             exchange=self.exchange,
                             routing_key=routing_key)
            logger.debug('[AMQP] Publish on %s', routing_key)
