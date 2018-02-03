from kafka import KafkaProducer
from .app import app
import json


def send_message(topic, domain, partition=0):
	producer = KafkaProducer(bootstrap_servers=app.config['KAFKA_SERVER'],
	                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
	future = producer.send(topic, domain, partition=partition)
	try:
		future.get(timeout=app.config['KAFKA_TIME_OUT'])
	except Exception as e:
		app.logger.error(e, exc_info=True)
