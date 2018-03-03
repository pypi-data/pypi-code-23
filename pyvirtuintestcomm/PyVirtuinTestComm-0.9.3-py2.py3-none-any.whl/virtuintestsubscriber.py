"""VirtuinTestSubscriber is used to subscribe to test's status updates
over AMQP (via RabbitMQ).
"""
import json
import pika


# pylint: disable=too-many-instance-attributes
class VirtuinTestSubscriber(object):
    """VirtuinTestSubscriber is used to subscribe to test's status updates
    over AMQP (via RabbitMQ).

    Attributes:
        None
    """
    def __init__(self, stationName):
        self.version = '0.9.3'
        self.exName = '{:s}'.format(stationName)
        self.conn = None
        self.ch = None
        self.qName = None
        self.isOpen = False
        self.isSubscribing = False
        self.subscriber = None
        self.subscribeTag = None

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
        self.ch.exchange_declare(exchange=self.exName, exchange_type='fanout')
        q = self.ch.queue_declare(queue='', exclusive=True, durable=False)
        qName = q.method.queue
        self.ch.queue_bind(queue=qName, exchange=self.exName)
        self.qName = qName
        self.isOpen = True

    def close(self):
        """Close connection to RabbitMQ
        Args:
            None
        Returns:
            None
        """
        if self.isOpen:
            return
        if self.isSubscribing:
            self.unsubscribe()
        if self.conn:
            self.conn.close()
        self.conn = None
        self.ch = None
        self.qName = None
        self.isSubscribing = False
        self.subscriber = None
        self.subscribeTag = None
        self.isOpen = False

    # pylint: disable=unused-argument
    def _consume(self, ch, method, props, body):
        """Callback routine for incoming status updates.
        This is set in subscribe(). Subsequently calls
        subscriber callback routine with dict result.
        Args:
            ch (str): RabbitMQ channel
            method: RabbitMQ method
            props: RabbitMQ props
            body: RabbitMQ Payload
        Returns:
            None
        """
        if self.subscriber and callable(self.subscriber):
            try:
                jsonData = json.loads(body.decode('utf8'))
                self.subscriber(None, jsonData)
            # pylint: disable=broad-except
            except Exception as err:
                self.subscriber(err, None)

    def consume(self):
        """Gets next broadcast packet. This method does not block.
        If no packet available, returns None
        Args:
            None
        Returns:
            dict|None: Status packet or None
        """
        if not self.isOpen:
            raise Exception('Connection not open.')
        method, _, body = self.ch.basic_get(queue=self.qName)
        if method:
            jsonData = json.loads(body.decode('utf8'))
            return jsonData
        return None

    def subscribe(self, subscriber):
        """Subscribes using callback. This method blocks.
        To release, call unsubscribe in callback function.
        Args:
            subscriber (callable): Callback function triggered when
            status updates received. cb(err, result) => None
        Returns:
            str: subscription consumer tag
        """
        try:
            if not self.isOpen or self.isSubscribing:
                raise Exception('Connection not open or already subscribing.')
            self.isSubscribing = True
            self.subscriber = subscriber
            self.subscribeTag = self.ch.basic_consume(self._consume, queue=self.qName)
            self.ch.start_consuming()  # This blocks
            return self.subscribeTag
        # pylint: disable=broad-except,unused-variable
        except Exception as err:
            return self.subscribeTag

    def unsubscribe(self):
        """Stop subscribing to test status updates.
        Args:
            None
        Returns:
            None
        """
        if not self.open or not self.isSubscribing:
            return None
        self.ch.basic_cancel(self.subscribeTag)
        self.subscriber = None
        self.isSubscribing = False
        self.subscribeTag = None
        return None
