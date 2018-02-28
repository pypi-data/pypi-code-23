import json

import kafka
import logging as LOG


class KafkaBrokerPublisher():
    def __init__(self, host, port, topic):
        self.kafka_client = None
        self.kafka_server = None

        self.host = host
        self.port = port
        self.topic = topic

        try:
            self._get_client()
            self._get_server()
        except Exception as e:
            LOG.exception("Failed to connect to Kafka service: %s", e)

    def _get_client(self):
        if not self.kafka_client:
            self.kafka_client = kafka.KafkaClient(
                "%s:%s" % (self.host, self.port))
            self.kafka_producer = kafka.SimpleProducer(self.kafka_client)

    def _get_server(self):
        if not self.kafka_server:
           self.kafka_server = kafka.KafkaClient(
                "%s:%s" % (self.host, self.port))
           self.kafka_consumer = kafka.KafkaConsumer(self.topic,bootstrap_servers = ["%s:%s" % (self.host, self.port)])

    def send(self, data):
        try:
            self.kafka_producer.send_messages(
                self.topic, json.dumps(data).encode("utf-8"))
        except Exception as e:
            LOG.exception(("Failed to send sample data: %s"), e)
            raise
