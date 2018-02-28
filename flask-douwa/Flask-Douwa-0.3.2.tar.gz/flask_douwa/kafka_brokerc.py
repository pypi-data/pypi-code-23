import msgpack
import confluent_kafka
from confluent_kafka import KafkaError, KafkaException

api_version_request = True


def read_notification_from_ceilometer_over_kafka(conf, topic, pid, callbacks):
    print('Using confluent_kafka module version %s (0x%x)' % confluent_kafka.version())
    print('Using librdkafka version %s (0x%x)' % confluent_kafka.libversion())

    default_conf = {'group.id': pid,
            'session.timeout.ms': 6000,
            'enable.auto.commit': False,
            'client.id':'kafka-python-1.3.5',
            'ssl.key.password':'KafkaOnsClient',
            'ssl.certificate.location':'/Users/iye/project/oauth/oauth/kafka.client.truststore.jks',
            'default.topic.config': {
                 'auto.offset.reset': 'earliest'
            }}
    conf.update(default_conf)
    consumer = confluent_kafka.Consumer(**conf)
    consumer.subscribe(topic)
    try:
        while True:
            msg = consumer.poll(timeout=10)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    raise KafkaException(msg.error())
            else:
                data = None
                if msg.value():
                    data = msgpack.loads(msg.value(), encoding='utf-8')
                    if data:
                        t = msg.topic()
                        if t and t in callbacks:
                            commit = callbacks[msg.topic()](data)
                            if commit:
                                consumer.commit(msg, async=True)
    except KeyboardInterrupt:
        print('%% Aborted by user\n')
    consumer.close()


def send_message(conf, topic, message):

        default_conf = {'api.version.request': api_version_request,
            'client.id':'kafka-python-1.3.5',
            'ssl.key.password':'KafkaOnsClient',
            'ssl.certificate.location':'/Users/iye/project/oauth/oauth/kafka.client.truststore.jks',
                        'default.topic.config': {'produce.offset.report': True}
                        }
        conf.update(default_conf)
        p = confluent_kafka.Producer(**conf)

        try:
            p.produce(topic, value=msgpack.dumps(message, use_bin_type=True))
            p.poll(0)
        except BufferError as e:
            print('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                            len(p))
        p.flush()


if __name__ == '__main__':
    bootstrap_servers = "kafka-ons-internet.aliyun.com:8080"
    topic = 'ptopic'
    send_message(conf, topic, {"hello":"world"})
    print(get_message(topic))
