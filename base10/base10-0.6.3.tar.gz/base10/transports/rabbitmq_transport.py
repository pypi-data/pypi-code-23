from base10.base import Reader, Writer


class RabbitMQTransport(object):
    def __init__(
        self,
        broker='127.0.0.1',
        port=5672,
        virtual_host='/',
        exchange='amq.topic',
        queue_name=None,
        username='guest',
        password='guest'
    ):
        try:
            self._pika = __import__('pika')
        except ImportError:
            from base10.exceptions import Base10Error
            raise Base10Error(
                'RabbitMQReader and RabbitMQWriter require the pika module'
            )

        if queue_name is None:
            from uuid import uuid1 as uuid
            queue_name = str(uuid())

        self._broker = broker
        self._port = port
        self._virtual_host = virtual_host
        self._exchange = exchange
        self._queue_name = queue_name
        self._username = username
        self._password = password

        self._connect()

    def _connect(self):
        credentials = self._pika.PlainCredentials(
            self._username, self._password
        )
        parameters = self._pika.ConnectionParameters(
            self._broker, self._port, self._virtual_host, credentials
        )
        connection = self._pika.BlockingConnection(parameters)
        self._channel = connection.channel()


class RabbitMQReader(RabbitMQTransport, Reader):
    def __init__(self, routing_key='metrics.#', auto_delete=True, **kwargs):
        super(RabbitMQReader, self).__init__(**kwargs)

        self._channel.queue_declare(self._queue_name, auto_delete=auto_delete)
        self._channel.queue_bind(self._queue_name, self._exchange, routing_key)

    def read(self):
        for method_frame, _, body in self._channel.consume(self._queue_name):
            self._channel.basic_ack(method_frame.delivery_tag)
            yield body


class RabbitMQWriter(RabbitMQTransport, Writer):
    def __init__(self, topic='metrics.all', **kwargs):
        super(RabbitMQWriter, self).__init__(**kwargs)

        self._topic = topic

    def write(self, string):
        try:
            self._channel.publish(self._exchange, self._topic, string)
        except pika.exceptions.ChannelClosed:
            self._connect()
            self._channel.publish(self._exchange, self._topic, string)
