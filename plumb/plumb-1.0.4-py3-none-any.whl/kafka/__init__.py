"""
Source and Sink implementations, using a Kafka Consumer instance and a Kafka Producer instance, respectively.
"""

import logging

from confluent_kafka import Consumer, KafkaError, Producer

from ..serializers import JSON

__all__ = ['Source', 'Sink']


class Source(JSON):
    """
    Uses a connected Kafka broker to poll messages from.
    """

    CONSUMER_DEFAULT_SETTINGS = {
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }

    def __str__(self):
        return "plumb.kafka.Source(settings={}, topics={})".format(self.consumer_settings, self.topics)

    def __init__(self, settings, topics):
        """
        :param settings: Settings dictionary to pass to the confluent_kafka.Consumer constructor.
                         'bootstrap.servers' and 'group.id' keys should be present.
        :param topics: List of topics the consumer will subscribe to.
        """
        if not all(required in settings for required in ('bootstrap.servers', 'group.id')):
            raise ValueError("'bootstrap.servers' and 'group.id' settings are mandatory.")
        self.consumer_settings = self.CONSUMER_DEFAULT_SETTINGS.copy()
        self.consumer_settings.update(settings)
        self.consumer = Consumer(self.consumer_settings)
        self.consumer.subscribe(topics)
        self.log = logging.getLogger('plumb.kafka.consumer'.format(self.consumer_settings['group.id']))
        self.log.info('Starting Consumer with group.id {}'.format(self.consumer_settings['group.id']))

    def get(self, timeout=0.1):
        """
        Blocks until a valid message is retrieved from topic.
        Poll the topic for "timeout" seconds.
        """
        while True:
            try:
                msg = self.consumer.poll(timeout)
                if msg is None:
                    continue
                elif not msg.error():
                    return self.deserialize(msg.value().decode('utf-8'))
                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    self.log.debug('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
                    continue
                else:
                    self.log.error('Error occurred: {0}'.format(msg.error().str()))
                    continue
            except Exception as e:
                self.log.error(e)
                continue

    def close(self):
        """
        Callers SHOULD call this method in application code before exiting, in order to start consumer group rebalance inmediately.
        """
        self.log.info("Shutting down Consumer with group.id {}".format(self.consumer_settings['group.id']))
        self.consumer.close()


class Sink(JSON):
    """
    Uses a connected Kafka broker to produce messages in a topic.
    """

    PRODUCER_DEFAULT_SETTINGS = {
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }

    def __str__(self):
        return "plumb.kafka.Sink(settings={}, topic_name={})".format(self.producer_settings, self.topic_name)

    def __init__(self, settings, topic_name):
        """
        :param settings: Settings dictionary to pass to the confluent_kafka.Producer constructor.
                         'bootstrap.servers' key should be present.
        :param topic_name: Topic the producer will produce messages to.
        """
        self.producer_settings = self.PRODUCER_DEFAULT_SETTINGS.copy()
        self.producer_settings.update(settings)
        self.topic_name = topic_name
        self.producer = Producer(self.producer_settings, self.topic_name)
        self.log = logging.getLogger('plumb.kafka.producer.{}'.format(self.topic_name))
        self.log.info('Starting Producer for topic {}'.format(self.topic_name))

    def put(self, message):
        """
        Produce a message in the specified topic.
        :param message: A byte-like object.
        :return: None
        """
        try:
            self.producer.produce(self.topic_name, bytes(self.serialize(message), "utf-8"))
            self.producer.poll(0)  # Notify delivery
        except Exception as e:
            self.log.error(e)

    def close(self, timeout=5):
        """
        Callers SHOULD call this method in application code before exiting, in order to ensure delivery of pending messages.
        """
        self.producer.flush(timeout)
