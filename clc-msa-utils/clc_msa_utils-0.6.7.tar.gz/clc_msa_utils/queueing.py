import json
import logging
import threading
import traceback

import pika


class QueueConsumer:
    _config = {}
    _logger = logging.getLogger('QueueConsumer')
    _connection = None
    _channel = None
    _callback = None
    _worker_thread = None

    def __init__(self, config={}):
        self._config = config
        self._setup_logging()

    def _setup_logging(self):
        numeric_level = logging.DEBUG
        if self._config.get('logging_level'):
            numeric_level = getattr(logging, self._config.get('logging_level'), logging.INFO)
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        self._logger.setLevel(numeric_level)

    def _configure_listener(self):
        if 'auth' not in self._config \
                or 'user' not in self._config['auth'] \
                or 'password' not in self._config['auth'] \
                or 'queue' not in self._config \
                or 'host' not in self._config \
                or 'port' not in self._config:
            self._logger.error("config=" + str(self._config))
            raise Exception("Expected the consumer configuration to have an auth.user, "
                            "auth.password, host, queue, and port attribute, but received: {0}"
                            .format(str(self._config)))
        credentials = pika.PlainCredentials(self._config['auth']['user'], self._config['auth']['password'])
        parameters = pika.ConnectionParameters(self._config['host'], self._config['port'], '/', credentials)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._config['queue'], durable=True)

        if 'exchange' in self._config:
            self._channel.queue_bind(queue=self._config['queue'], exchange=self._config['exchange']['name'],
                                     routing_key=self._config['binding_key'])

        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self._callback, queue=self._config['queue'])

        self._channel.start_consuming()

    def get_config(self):
        return self._config

    def listen(self, callback, blocking=True):
        self._callback = callback

        if blocking:
            self._logger.debug("Creating blocking listener.")
            self._configure_listener()
        else:
            self._logger.debug("Creating non-blocking listener.")
            self._worker_thread = threading.Thread(target=self._configure_listener)
            self._worker_thread.start()

    def stop_consuming(self):
        try:
            if not self._channel.is_closed:
                self._channel.stop_consuming()
                self._logger.debug("Channel stopped consuming on '{0}' thread.".format(self._config.get('name')))
            if not self._channel.is_closed:
                self._channel.close()
            self._logger.debug("Channel closed on '{0}' thread.".format(self._config.get('name')))
        except:
            self._logger.error(traceback.format_exc())

        try:
            if not self._connection.is_closed:
                self._connection.close()
            self._logger.debug("Connection closed on '{0}' thread.".format(self._config.get('name')))
        except:
            self._logger.error(traceback.format_exc())

    def thread(self):
        return self._worker_thread

    def config(self):
        return self._config

    def callback(self):
        return self._callback


class QueueProducer:
    _config = {}
    _logger = logging.getLogger('QueueProducer')
    _connection = None
    _queue_channel = None

    def __init__(self, config={}):
        self._config = self._normalize_config(config)
        self._setup_logging()
        self._configure_producer()

    def _setup_logging(self):
        numeric_level = logging.DEBUG
        if self._config.get('logging_level'):
            numeric_level = getattr(logging, self._config.get('logging_level'), logging.INFO)
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        self._logger.setLevel(numeric_level)

    def _configure_producer(self):
        self._logger.debug("Configuring queue producer with config:\n%s" % self._config)
        if not self._connection or self._connection.is_closed:
            credentials = pika.PlainCredentials(self._config['auth']['user'], self._config['auth']['password'])
            parameters = pika.ConnectionParameters(self._config['host'], self._config['port'], '/', credentials)
        if not self._queue_channel or self._queue_channel.is_closed:
            self._connection = pika.BlockingConnection(parameters)
            self._queue_channel = self._connection.channel()

            if 'create' in self._config['exchange'] and self._config['exchange']['create']:
                self._logger.debug("Exchange is being ensured present based on configuration...")
                self._queue_channel \
                    .exchange_declare(exchange=self._config['exchange']['name'],
                                      exchange_type=(
                                          self._config['exchange']['type'] if 'type' in self._config[
                                              'exchange'] else 'direct'),
                                      arguments=(self._config['exchange']['arguments'] if 'arguments' in
                                                                                          self._config[
                                                                                              'exchange'] else {}),
                                      durable=(
                                          self._config['exchange']['durable'] if 'durable' in self._config[
                                              'exchange'] else True))

    def _normalize_config(self, config):
        return config

    def publish(self, message=None):
        self._logger.info("Publishing message to exchange '%s' with binding key '%s'" % (
            self._config['exchange']['name'], self._config['binding_key']))
        self._logger.debug("Message:\n%s" % json.dumps(message, indent=4))
        self._configure_producer()
        self._queue_channel.basic_publish(exchange=self._config['exchange']['name'],
                                          routing_key=(
                                              self._config['binding_key'] if 'binding_key' in self._config else '#'),
                                          body=json.dumps(message),
                                          properties=pika.BasicProperties(delivery_mode=2,  # make message persistent
                                                                          content_type='application/json'))

    def get_config(self):
        return self._config


class QueueFactory:
    """
    QueueFactory provides helper methods for simply passing in a configuration
    and having producers/consumers created based on that config.  Additionally,
    there will be builder style methods available for setting/overriding configuration
    prior to generating producers/consumers.

    Currently, this solution is satisfying making a connection using AMQP which is compatible with
    RabbitMQ and ActiveMQ.  It could be enhanced to provide further abstraction and provide
    connections to other Queue services in theory.
    """

    _logger = logging.getLogger('QueueFactory')

    def __init__(self, monitoring_period_seconds=10):
        self._consumers = {}
        self._producers = {}
        self._config = {}
        self._monitoring = False
        self._monitoring_period_seconds = monitoring_period_seconds
        self._monitoring_thread = None
        self._setup_logging()
        self._logger.info("Initializing QueueFactory...")

    def _setup_logging(self):
        numeric_level = logging.DEBUG
        if self._config.get('logging_level'):
            numeric_level = getattr(logging, self._config.get('logging_level'), logging.INFO)
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        self._logger.setLevel(numeric_level)

    def create_consumers(self, queue_config):
        """
        Example Consumer Queue Configuration:
        {
          "queue_config": [
            {
              "name": "name-to-reference-this-connection",
              "type": "consumer",
              "exchange": {
                "name": "name-of-exchange",
                "type": "direct | fanout | etc",
                "arguments": {"x-delayed-type": "topic"},
                "durable": true | false
              },
              "queue": "name-of-queue",
              "binding_key": "#",
              "host": "rabbitmq-host",
              "port": "5672",
              "auth": {
                "user": "guest",
                "password": "guest"
              }
            }
          ]
        }
        """

        if 'queue_config' in queue_config:
            queue_config = queue_config['queue_config']

        self._logger.debug("Setting up consumers for the following configuration:\n%s" % str(queue_config))
        for config in queue_config:
            if 'type' in config and 'consumer' == config['type']:
                consumer = QueueConsumer(config)
                self._logger.debug("Adding configuration for configuration %s." % str(config['name']))
                self._consumers[config['name']] = consumer

        self._logger.debug("Created {0} consumers.".format(str(len(self._consumers))))
        for consumer in list(self._consumers.values()):
            self._logger.debug("Created {0} consumer.".format(consumer.config().get("name")))
        return self._consumers

    def create_producers(self, queue_config):
        """
        Example Producer Queue Configuration:
        {
            "queue_config": [
                {
                    "name": "name-to-reference-this-connection",
                    "type": "producer",
                    "exchange": {
                        "name": "name-of-exchange",
                        "create": true | false (whether or not to ensure exchange is present),
                        "type": "direct | fanout | etc",
                        "arguments": {"x-delayed-type": "topic"},
                        "durable": true | false
                    },
                    "binding_key": "#",
                    "host": "rabbitmq-host",
                    "port": "5672",
                    "auth": {
                        "user": "guest",
                        "password": "guest"
                    }
                }
            ]
        }
        """

        self._logger.debug("Setting up producers for the following configuration:\n%s" % queue_config)
        if 'queue_config' in queue_config:
            queue_config = queue_config['queue_config']

        for config in queue_config:
            if 'type' in config['exchange'] and 'producer' == config['exchange']['type']:
                producer = QueueProducer(config)
                self._producers[config['name']] = producer

        return self._producers

    def stop_consuming(self):
        """
        Stops all QueueConsumers from consuming.
        """
        self.stop_monitoring()

        for consumer in list(self._consumers.values()):
            consumer.stop_consuming()

        for consumer in list(self._consumers.values()):
            consumer.stop_consuming()
        self._consumers = {}

    def start_consuming(self, callback):
        """
        Starts all QueueConsumers consuming in a separate thread.
        """
        for consumer in list(self._consumers.values()):
            consumer.listen(callback, blocking=False)
        self.start_monitoring()

    def consumers(self):
        """
        Gets a list of all QueueConsumers

        :return: list of QueueConsumers
        """
        return list(self._consumers.values())

    def start_monitoring(self):
        self._logger.debug("Thread Monitoring Enabled checking threads every {0} seconds."
                           .format(self._monitoring_period_seconds))
        self._monitoring = True
        self._monitoring_thread = threading.Timer(self._monitoring_period_seconds, self._monitor)
        self._logger.debug("Created monitoring thread named {0}."
                           .format(self._monitoring_thread.name))
        self._monitoring_thread.start()
        self._logger.debug("Monitoring thread started and is alive? {0}."
                           .format(str(self._monitoring_thread.is_alive())))

    def monitoring_thread(self):
        return self._monitoring_thread

    def stop_monitoring(self):
        self._logger.debug("Thread Monitoring Disabled")
        self._monitoring = False

    def _monitor(self):
        self._logger.debug("Monitoring {0} threads..."
                           .format(str(len(list(self._consumers.values())))))
        if self._monitoring:
            for consumer in list(self._consumers.values()):
                if not self._monitoring:
                    break
                if not consumer.thread().is_alive():
                    consumer.listen(consumer.callback(), blocking=False)
                    self._logger.debug("Consumer thread {0} was not alive, successfully started"
                                       .format(consumer.config().get("name")))
                else:
                    self._logger.debug("Consumer thread {0} is still active."
                                       .format(consumer.config().get("name")))

        if self._monitoring:
            self.start_monitoring()
        self._logger.debug("Done monitoring threads.")
