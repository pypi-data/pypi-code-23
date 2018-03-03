"""VirtuinTestViewServer is used to listen for view requests
over AMQP (via RabbitMQ).
"""

import json
import pika

# pylint: disable=too-many-instance-attributes,duplicate-code
class VirtuinTestViewServer(object):
    """VirtuinTestViewServer is used to listen for view requests
    over AMQP (via RabbitMQ).

    Attributes:
        None
    """
    def __init__(self, stationName, testName):
        self.stationName = stationName
        self.exName = '{:s}_view'.format(self.stationName)
        self.qName = testName
        self.conn = None
        self.ch = None
        self.isOpen = False
        self.isListening = False
        self.listener = None

    def open(self, hostName='localhost'):
        """Open connection to RabbitMQ
        Args:
            hostName (str): Address of broker
        Returns:
            None
        """
        connParams = pika.ConnectionParameters(host=hostName)
        self.conn = pika.BlockingConnection(connParams)
        self.ch = self.conn.channel()
        self.ch.exchange_declare(
            exchange=self.exName,
            exchange_type='direct',
            durable=False
        )
        self.ch.queue_declare(queue=self.qName, exclusive=True)
        self.ch.queue_bind(queue=self.qName, exchange=self.exName, routing_key=self.qName)
        self.ch.basic_qos(prefetch_count=1)
        self.isOpen = True

    def close(self):
        """Close connection to RabbitMQ
        Args:
            tearDown (bool, optional):
                To tear down RMQ exchange.
                Useful to clean environment.
        Returns:
            None
        """
        if self.isOpen:
            self.conn.close()
        self.conn = None
        self.ch = None
        self.isOpen = False
        self.isListening = False
        self.listener = None

    # pylint: disable=unused-argument
    def _consume(self, ch, method, props, body):
        """Callback routine for incoming payloads.
        This is set in listen(). Subsequently calls
        listener callback routine with dict result.
        Args:
            ch (str): RabbitMQ channel
            method: RabbitMQ method
            props: RabbitMQ props
            body: RabbitMQ Payload
        Returns:
            None
        """
        jsonData = json.loads(body.decode('utf8'))
        if self.listener and callable(self.listener):
            # pylint: disable=unused-variable
            rstDict = self.listener(jsonData) # noqa
        self.ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        """Gets next packet from client. This method does not block.
        If no packet available, returns None
        Args:
            None
        Returns:
            dict|None: Status packet or None
        """
        if not self.ch or not self.ch.is_open:
            return None, None, None, None
        method, _, body = self.ch.basic_get(queue=self.qName)
        if method:
            jsonData = json.loads(body.decode('utf8'))
            self.ch.basic_ack(method.delivery_tag)
            return jsonData
        return None

    def listen(self, listener):
        """Start listening for requests. This method blocks.
        Args:
            listener (callable): callback function called when
            request is received (error: str, result: dict) => dict
        Returns:
            str: consumerTag
        """
        try:
            consumerTag = None
            if not self.isOpen or self.isListening:
                return None
            self.listener = listener
            self.isListening = True
            consumerTag = self.ch.basic_consume(self._consume, queue=self.qName)
            self.ch.start_consuming()  # This blocks
            return consumerTag
        # pylint: disable=broad-except,unused-variable
        except Exception as err:
            return None

    def stopListening(self):
        """Stop listening for requests.
        Args:
            None
        Returns:
            str: consumerTag
        """
        if self.isOpen and self.isListening:
            self.ch.stop_consuming()
            self.isListening = False
            self.listener = False
