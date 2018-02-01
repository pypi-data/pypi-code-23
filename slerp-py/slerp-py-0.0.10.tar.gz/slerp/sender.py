from kafka import KafkaProducer
from app import app
from app import log


def send_message(topic, domain, partition=0):
	producer = KafkaProducer(bootstrap_servers=app.config['KAFKA_SERVER'], value_serializer=lambda v: json.dumps(v).encode('UTF-8'))
	future = producer.send(topic, domain, partition=partition)
	try:
		future.get(timeout=app.config['KAFKA_TIME_OUT'])
	except Exception as e:
		log.error(e, exc_info=True)